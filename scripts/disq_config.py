import os
import json


class DiSQ_Config:
    def __init__(self, dataset, modelname, modelurl, version, paraphrase, feature, hfpath, device_number):
        self.dataset = dataset
        self.modelname = modelname
        self.modelurl = modelurl
        self.version = version
        self.paraphrase = paraphrase
        self.feature = feature
        self.hfpath = hfpath
        self.modelname = modelname
        self.device_number = device_number

        if self.modelurl is not None: 
            # replace the modelname with the modelurl's 2nd part after '/'
            # for example, "meta-llama/Meta-Llama-3.1-8B" -> "Meta-Llama-3.1-8B"
            self.modelname = self.modelurl.split('/')[1]
        
        if self.paraphrase is None:
            from qa_utils import QAUtils
            self.QAUtils = QAUtils()
        elif self.paraphrase == 'p1':
            from qa_utils_p1 import QAUtils_P1
            self.QAUtils = QAUtils_P1()
        elif self.paraphrase == 'p2':
            from qa_utils_p2 import QAUtils_P2
            self.QAUtils = QAUtils_P2()
        
        if self.dataset == 'pdtb':
            fp = 'data/datasets/dataset_pdtb.json'
        elif self.dataset == 'ted':
            fp = 'data/datasets/dataset_TED.json'
        with open(fp, 'r') as f:
            self.data_dict = json.load(f)
        
        self.NUM_LEVEL2_RELATION = 11

        self.question_dir = 'data/questions'
        # Check if the directory exists, if not create it
        if not os.path.exists(self.question_dir):
            os.makedirs(self.question_dir)
        
        # In the format dataset_{}_prompt_{}
        self.taskname = 'dataset_{}_prompt_{}'.format(self.dataset, self.version)
        # If self.feature is None, then we append it to the end of the taskname
        if self.feature in ['conn', 'context']:
            self.taskname += '_{}'.format(self.feature)
        # If self.paraphrase is not None, then we append it to the end of the taskname
        if self.paraphrase is not None:
            self.taskname += '_{}'.format(self.paraphrase)
        if self.feature == 'history':
            self.taskname += '_{}_{}'.format(self.modelname, 'history')
        
        self.positive_tokens = ['Yes', 'yes', 'YES', 'True', 'true', 'TRUE', 'correct', 'Correct', 'CORRECT', 'positive', 'Positive', 'POSITIVE']
        self.negative_tokens = ['No', 'no', 'NO', 'False', 'false', 'FALSE', 'incorrect', 'Incorrect', 'INCORRECT', 'negative', 'Negative', 'NEGATIVE', 'IN', 'in']
        
        if self.modelname == '13bchat':
            self.model = "meta-llama/Llama-2-13b-chat-hf"
        if self.modelname == '13b':
            self.model = "meta-llama/Llama-2-13b-hf"
        if self.modelname == '7bchat':
            self.model = "meta-llama/Llama-2-7b-chat-hf"
        if self.modelname == '7b':
            self.model = "meta-llama/Llama-2-7b-hf"
        if self.modelname == 'vicuna-13b':
            self.model = "lmsys/vicuna-13b-v1.5"
        if self.modelname == 'wizard':
            self.model = None # Caveat: Wizard model has been taken down by the developers. We advise our users not to try these models. Check the discussion thread. https://huggingface.co/posts/WizardLM/329547800484476
        if self.modelname == 'wizard-code':
            self.model = None # Caveat: Wizard model has been taken down by the developers. We advise our users not to try these models. Check the discussion thread. https://huggingface.co/posts/WizardLM/329547800484476
        if self.modelname == 'wizard-math':
            self.model = None# Caveat: Wizard model has been taken down by the developers. We advise our users not to try these models. Check the discussion thread. https://huggingface.co/posts/WizardLM/329547800484476 
        
        if self.modelurl is not None:
            self.model = self.modelurl
        
        self.result_dir = 'data/results/{}_{}'.format(self.modelname, self.taskname)
        # When self.modelname is not none, check if the directory exists, if not create it
        if self.modelname is not None and not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
            print('Directory {} created.'.format(self.result_dir))
        
        # Create a json file for disq_score.json
        self.disq_score_fp = 'data/results/disq_score_{}.json'.format(self.dataset)

        # check if 'data/results' exists, if not create it
        if not os.path.exists('data/results'):
            os.makedirs('data/results')

        # check if the file exists, if not create it and initialize it with an empty dictionary
        if not os.path.exists(self.disq_score_fp):
            with open(self.disq_score_fp, 'w') as f:
                json.dump({}, f)

        self.disq_score_csv_fp = 'data/results/disq_score_{}.csv'.format(self.dataset)
        self.disq_score_best_csv_fp = 'data/results/disq_score_{}_best.csv'.format(self.dataset)

        # create a verbalization directory
        self.verbalization_dir = 'data/verbalizations'
        # check if the directory exists, if not create it
        if not os.path.exists(self.verbalization_dir):
            os.makedirs(self.verbalization_dir)
