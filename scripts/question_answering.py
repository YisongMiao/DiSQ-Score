import argparse
import os
import pickle
import json
from datetime import datetime

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

from disq_config import DiSQ_Config


class QA:
    def __init__(self, config):
        self.config = config
        
        # Load the questions
        self.taskname = self.config.taskname
        self.question_dir = self.config.question_dir
        self.question_fp = os.path.join(self.question_dir, f'{self.taskname}.json')
        with open(self.question_fp, 'r') as f:
            self.question_dict = json.load(f)
        
        # Load the model
        print('Loading the model...')
        print(self.config.model)
        print('Load the tokenizer')
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model, cache_dir=self.config.hfpath)
        print('Load the model')
        self.model = AutoModelForCausalLM.from_pretrained(self.config.model, cache_dir=self.config.hfpath)
        print('Model loaded, convert.')
        self.model = self.model.to(dtype=torch.float16) # Make it compatible with the GPU RAM

        # Try to use the GPU if available
        self.device =  torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device("cuda:{}".format(self.config.device_number))
        self.model.to(self.device)
        # Print the model config and device being used
        print('Model config: ', self.model.config)
        print('Device being used: ', self.device)
        print('QA class is initialized.')
    
    def decode_one_case(self, question, filename):
        print('Decoding the question: ', question)
        print('Filename: ', filename)
        
        input_ids = self.tokenizer(question, return_tensors="pt").input_ids.to(self.device)

        outputs = self.model.generate(input_ids, 
            max_new_tokens=1,
            output_scores=True, 
            return_dict_in_generate=True,
            do_sample=False,
            num_return_sequences=1)
        scores = outputs.scores

        probabilities = F.softmax(scores[0][0], dim=-1).cpu() # Because we only have and care about the first sequence, and the first token in the sequence
        # convert the probabilities to float
        probabilities = probabilities.float()

        prob_top30, idx_top30 = torch.topk(probabilities, 30) # To save space in disk, we only save the token and their probabilities for the top 30 tokens

        # Use self.tokenizer.decode to get the actual token
        actual_tokens = [self.tokenizer.decode([idx]) for idx in idx_top30]

        prob_top30 = prob_top30.tolist()
        instance_output = [actual_tokens, prob_top30]

        # Save the top 30 tokens and their probabilities into a pickle file with the filename under self.config.result_dir
        result_fp = os.path.join(self.config.result_dir, f'{filename}.pk')
        with open(result_fp, 'wb') as f:
            pickle.dump(instance_output, f)

    def loop_through(self):
        for instance_key, instance_value in self.question_dict.items():
            for pair_idx, questions in instance_value.items():
                targeted_question = questions['targeted_question'] # list of size 1
                counterfactual_question = questions['counterfactual_question'] # list of size 5
                converse_targeted_question = questions['converse_targeted_question'] # list of size 1
                converse_counterfactual_question = questions['converse_counterfactual_question'] # list of size 5

                for qidx, question in enumerate(targeted_question):
                    filename = 'D-{}-e-{}-TQ-{}'.format(instance_key, pair_idx, qidx)
                    self.decode_one_case(question, filename)
                
                for qidx, question in enumerate(counterfactual_question):
                    filename = 'D-{}-e-{}-CQ-{}'.format(instance_key, pair_idx, qidx)
                    self.decode_one_case(question, filename)
                
                for qidx, question in enumerate(converse_targeted_question):
                    filename = 'D-{}-e-{}-CTQ-{}'.format(instance_key, pair_idx, qidx)
                    self.decode_one_case(question, filename)
                
                for qidx, question in enumerate(converse_counterfactual_question):
                    filename = 'D-{}-e-{}-CCQ-{}'.format(instance_key, pair_idx, qidx)
                    self.decode_one_case(question, filename)
                

if __name__ == '__main__':
    print('Start')

    parser = argparse.ArgumentParser()
    # model name
    parser.add_argument('--dataset', type=str, default='pdtb', help='pdtb or ted?')
    parser.add_argument('--modelname', type=str, default='13bchat', help='None (does not care which modle we deal with), only applicable for using historical QA: 13b, 13bchat, vicuna.')
    parser.add_argument('--modelurl', type=str, default=None, help='modelurl specific the models path in the hugging face model hub (for example, "meta-llama/Meta-Llama-3.1-8B"). modelurl has the right to overwrite modelname. If modelurl is provided, modelname will be ignored. It is used for new models that has not been specified in the config file.')
    parser.add_argument('--version', type=str, default='v1', help='v1, v2, v3, or v4?')
    parser.add_argument('--paraphrase', type=str, default=None, help='Options: None (default), p1, or p2 (paraphrasing to our original questions)')
    parser.add_argument('--feature', type=str, default=None, help='Options: conn, context, or history. Due to dataset characteristics, conn and context are only applicable to PDTB.')
    parser.add_argument('--hfpath', type=str, default='YOUR_PATH', help='The cache_dir for the Hugging Face model.')
    parser.add_argument('--device_number', type=int, default=0, help='Options: 0, 1, 2, 3, 4, 5, 6, 7. Default is 0.')

    p = parser.parse_args()

    # Create a new config file
    new_disq_config = DiSQ_Config(dataset=p.dataset, modelname=p.modelname, modelurl=p.modelurl, version=p.version, paraphrase=p.paraphrase, feature=p.feature, hfpath=p.hfpath, device_number=p.device_number)

    new_qa = QA(new_disq_config)
    new_qa.loop_through()
