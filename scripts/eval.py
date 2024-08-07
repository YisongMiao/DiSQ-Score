import argparse
import os
import pickle
import json
from datetime import datetime
from collections import defaultdict
import pandas as pd
import csv

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

from disq_config import DiSQ_Config
from sklearn.metrics import accuracy_score


class Eval:
    def __init__(self, config, verbalize):
        self.config = config
        self.verbalize = verbalize
        
        # Load the questions
        self.taskname = self.config.taskname
        self.question_dir = self.config.question_dir
        self.question_fp = os.path.join(self.question_dir, f'{self.taskname}.json')
        with open(self.question_fp, 'r') as f:
            self.question_dict = json.load(f)

        # Load results
        self.modelname = self.config.modelname
        self.result_dir = self.config.result_dir
        self.data_dict = self.config.data_dict
        self.disq_score_fp = self.config.disq_score_fp

        with open(self.disq_score_fp, 'r') as f:
            self.disq_score_dict = json.load(f)

        self.init_dataset_stats()

        self.current_disq_score_dict = {}
        self.current_disq_score_dict['modelname'] = self.modelname
        self.current_disq_score_dict['version'] = self.config.version
        self.current_disq_score_dict['paraphrase'] = self.config.paraphrase
        self.current_disq_score_dict['feature'] = self.config.feature
    
    def init_dataset_stats(self):
        # Loop through the data_dict and initialize the stats
        # To do so, we get the mapping between keys and the DR field
        self.id2DR = {}
        for key in self.data_dict:
            DR = self.data_dict[key]['DR']
            DR = '.'.join(DR.split('.')[:2])
            if self.data_dict[key]['DR'] == 'Contingency.Cause.Result':
                DR = 'Contingency.Result'
            if self.data_dict[key]['DR'] == 'Contingency.Cause.Reason':
                DR = 'Contingency.Reason'
            
            self.id2DR[int(key)] = DR
        # Get the DR2id, which is a dict of list
        self.DR2id = {}
        for key in self.id2DR:
            DR = self.id2DR[key]
            if DR not in self.DR2id:
                self.DR2id[DR] = []
            self.DR2id[DR].append(key)
        # Sort the self.DR2id by the length of the list
        self.DR2id = {k: v for k, v in sorted(self.DR2id.items(), key=lambda item: len(item[1]), reverse=True)}
        # print the length of the DR2id
        for key in self.DR2id:
            print(key, len(self.DR2id[key]))

        self.level2_relation = ['Comparison.Concession', 'Comparison.Contrast', 'Contingency.Reason', 'Contingency.Result', 'Expansion.Conjunction', 'Expansion.Equivalence', 'Expansion.Instantiation', 'Expansion.Level-of-detail', 'Expansion.Substitution', 'Temporal.Asynchronous', 'Temporal.Synchronous']

    def process_prob(self, fp):
        with open(fp, 'rb') as f:
            instance_output = pickle.load(f)
        tokens = instance_output[0]
        probabilities = instance_output[1]
        token2prob = defaultdict(float)
        for idx, token in enumerate(tokens):
            token2prob[token] += probabilities[idx]
        # Get the positive probability by looping through the positive tokens
        positive_prob = 0
        for token in self.config.positive_tokens:
            positive_prob += token2prob[token]
        # Get the negative probability by looping through the negative tokens
        negative_prob = 0
        for token in self.config.negative_tokens:
            negative_prob += token2prob[token]
        # If the positive probability is greater than the negative probability, then return 1, else return 0
        if positive_prob > negative_prob:
            return 1
        else:
            return 0

    def eval_all_level2_relations(self):
        for level2_relation in self.level2_relation:
            print('Evaluating level2_relation:', level2_relation)
            self.loop_through(desired_DR=level2_relation)

    
    def loop_through(self, desired_DR):
        TQ_is_YES_GT_list = []
        TQ_is_YES_list = []
        CQ_is_YES_GT_list = []
        CQ_is_YES_list = []
        CTQ_is_YES_GT_list = []
        CTQ_is_YES_list = []
        CCQ_is_YES_GT_list = []
        CCQ_is_YES_list = []
        TQ_consistency_count, TQ_consistency_total = 0, 0
        CQ_consistency_count, CQ_consistency_total = 0, 0

        results_consolidated = dict()

        index_for_desired_DR = []
        if desired_DR is not None:
            index_for_desired_DR = self.DR2id[desired_DR]
            # convert them to integer
            index_for_desired_DR = [int(idx) for idx in index_for_desired_DR]
        else:
            # the whole set
            index_for_desired_DR = self.data_dict.keys()
            # convert them to integer
            index_for_desired_DR = [int(idx) for idx in index_for_desired_DR]

        for instance_key, instance_value in self.question_dict.items():
            desired_Q = 'contributed to the same situation'
            if int(instance_key) not in index_for_desired_DR:
                continue
            for pair_idx, questions in instance_value.items():
                targeted_question = questions['targeted_question'] # list of size 1
                counterfactual_question = questions['counterfactual_question'] # list of size 5
                converse_targeted_question = questions['converse_targeted_question'] # list of size 1
                converse_counterfactual_question = questions['converse_counterfactual_question'] # list of size 5

                current_TQ = []
                current_CQ = []
                current_CTQ = []
                current_CCQ = []

                for qidx, question in enumerate(targeted_question):
                    filename = 'D-{}-e-{}-TQ-{}'.format(instance_key, pair_idx, qidx)
                    result_fp = os.path.join(self.result_dir, f'{filename}.pk')
                    answer = self.process_prob(result_fp)
                    results_consolidated[filename] = answer
                    TQ_is_YES_GT_list.append(1)
                    TQ_is_YES_list.append(answer)
                    current_TQ.append(answer)

                for qidx, question in enumerate(counterfactual_question):
                    filename = 'D-{}-e-{}-CQ-{}'.format(instance_key, pair_idx, qidx)
                    result_fp = os.path.join(self.result_dir, f'{filename}.pk')
                    answer = self.process_prob(result_fp)
                    results_consolidated[filename] = answer
                    CQ_is_YES_GT_list.append(0)
                    CQ_is_YES_list.append(answer)
                    current_CQ.append(answer)
                
                for qidx, question in enumerate(converse_targeted_question):
                    filename = 'D-{}-e-{}-CTQ-{}'.format(instance_key, pair_idx, qidx)
                    result_fp = os.path.join(self.result_dir, f'{filename}.pk')
                    answer = self.process_prob(result_fp)
                    results_consolidated[filename] = answer
                    CTQ_is_YES_GT_list.append(1)
                    CTQ_is_YES_list.append(answer)
                    current_CTQ.append(answer)
                
                for qidx, question in enumerate(converse_counterfactual_question):
                    filename = 'D-{}-e-{}-CCQ-{}'.format(instance_key, pair_idx, qidx)
                    result_fp = os.path.join(self.result_dir, f'{filename}.pk')
                    answer = self.process_prob(result_fp)
                    results_consolidated[filename] = answer
                    CCQ_is_YES_GT_list.append(0)
                    CCQ_is_YES_list.append(answer)
                    current_CCQ.append(answer)
                
                # Check the consistency of the current_TQ against the current_CTQ
                for idx in range(len(current_TQ)):
                    if current_TQ[idx] == current_CTQ[idx]:
                        TQ_consistency_count += 1
                    TQ_consistency_total += 1
                # Check the consistency of the current_CQ against the current_CCQ
                for idx in range(len(current_CQ)):
                    if current_CQ[idx] == current_CCQ[idx]:
                        CQ_consistency_count += 1
                    CQ_consistency_total += 1
        
        # Let's summarize the results
        # targeted score is the accuracy of the targeted questions
        TQ_accuracy = accuracy_score(TQ_is_YES_GT_list, TQ_is_YES_list)
        CTQ_accuracy = accuracy_score(CTQ_is_YES_GT_list, CTQ_is_YES_list)
        targeted_score = accuracy_score(TQ_is_YES_GT_list + CTQ_is_YES_GT_list, TQ_is_YES_list + CTQ_is_YES_list)
        # counterfactual score is the accuracy of the counterfactual questions
        CQ_accuracy = accuracy_score(CQ_is_YES_GT_list, CQ_is_YES_list)
        CCQ_accuracy = accuracy_score(CCQ_is_YES_GT_list, CCQ_is_YES_list)
        counterfactual_score = accuracy_score(CQ_is_YES_GT_list + CCQ_is_YES_GT_list, CQ_is_YES_list + CCQ_is_YES_list)
        # consistency is the portion of TQ_consistency_count over TQ_consistency_total and CQ_consistency_count over CQ_consistency_total
        TQ_consistency = TQ_consistency_count / TQ_consistency_total
        CQ_consistency = CQ_consistency_count / CQ_consistency_total
        TQ_percent = TQ_consistency_total / (TQ_consistency_total + CQ_consistency_total)
        CQ_percent = CQ_consistency_total / (TQ_consistency_total + CQ_consistency_total)
        overall_consistency = TQ_consistency * TQ_percent + CQ_consistency * CQ_percent

        disq_score = targeted_score * counterfactual_score * overall_consistency

        # Let's round the numbers to 3 decimal points
        TQ_accuracy = round(TQ_accuracy, 3)
        CQ_accuracy = round(CQ_accuracy, 3)
        TQ_consistency = round(TQ_consistency, 3)
        CQ_consistency = round(CQ_consistency, 3)
        targeted_score = round(targeted_score, 3)
        counterfactual_score = round(counterfactual_score, 3)
        overall_consistency = round(overall_consistency, 3)
        disq_score = round(disq_score, 3)

        # print the number of TQ, CQ, CTQ and CCQ
        print('TQ:', len(TQ_is_YES_GT_list))
        # print('CQ:', len(CQ_is_YES_GT_list))
        # print('CTQ:', len(CTQ_is_YES_GT_list))
        # print('CCQ:', len(CCQ_is_YES_GT_list))

        # Let's print
        print('TQ_accuracy:', TQ_accuracy)
        print('CTQ_accuracy:', CTQ_accuracy)
        print('targeted_score:', targeted_score)
        print('conterfactual_score:', counterfactual_score)
        print('overall_consistency:', overall_consistency)
        print('disq_score:', disq_score)

        if desired_DR is None:
            self.current_disq_score_dict['Overall'] = disq_score
            self.current_disq_score_dict['Targeted'] = targeted_score
            self.current_disq_score_dict['Counterfactual'] = counterfactual_score
            self.current_disq_score_dict['Consistency'] = overall_consistency
        else:
            self.current_disq_score_dict[desired_DR] = disq_score
        
        # Let's save results_consolidated if the desired_DR is None
        if desired_DR is None:
            fp = os.path.join(self.result_dir, 'results_consolidated.json')
            with open(fp, 'w') as f:
                json.dump(results_consolidated, f, indent=4)
            print('Results saved to:', fp)
    
    def save_results(self):
        # Save the results
        self.disq_score_dict['{}_{}'.format(self.taskname, self.modelname)] = self.current_disq_score_dict
        with open(self.disq_score_fp, 'w') as f:
            json.dump(self.disq_score_dict, f, indent=4)
        print('Results saved to:', self.disq_score_fp)

        # Dump self.disq_score_dict to a csv file
        df = pd.DataFrame(self.disq_score_dict)
        df = df.T
        # Give the first column a name as "taskcode"
        df.index.name = 'taskcode'
        df.to_csv(self.config.disq_score_csv_fp)
        print('Results saved to:', self.config.disq_score_csv_fp)

        # Let's also save the best results
        # It only works for the scenario where self.feature is None and self.paraphrase is None, we first check, otherwise, we skip
        if self.config.feature is not None or self.config.paraphrase is not None:
            return
        # we load the csv file
        df = pd.read_csv(self.config.disq_score_csv_fp)
        # we get all unique modelname
        modelnames = df['modelname'].unique()
        # create a new df, which takes the same columns as the original one
        df_best = pd.DataFrame(columns=df.columns)

        # for each modelname, we get the rows were paraprase is None and feature is None
        for modelname in modelnames:
            df_model = df[df['modelname'] == modelname]
            df_model = df_model[df_model['feature'].isnull()]
            df_model = df_model[df_model['paraphrase'].isnull()]
            # we get the best score
            best_score = df_model['Overall'].max()
            # we get the row where the Overall is equal to the best_score
            best_row = df_model[df_model['Overall'] == best_score]
            # we append the best_row to df_best
            df_best = df_best._append(best_row)
        # we save the df_best to the csv file, ignore the index
        df_best.to_csv(self.config.disq_score_best_csv_fp, index=False)
    
    def verbose(self):
        # read the best csv file
        df = pd.read_csv(self.config.disq_score_best_csv_fp)

        # get the row where the modelname is equal to the modelname
        row = df[df['modelname'] == self.modelname]

        verbalization = ''
        verbalization += '=== The results for model: {} ===\n'.format(self.modelname)
        # add the dataset information
        verbalization += 'Dataset: {}\n'.format(self.config.dataset)
        # add the disq_score
        verbalization += 'DiSQ Score: {}\n'.format(row['Overall'].values[0])
        # add the targeted score
        verbalization += 'Targeted Score: {}\n'.format(row['Targeted'].values[0])
        # add the counterfactual score
        verbalization += 'Counterfactual Score: {}\n'.format(row['Counterfactual'].values[0])
        # add the consistency
        verbalization += 'Consistency: {}\n'.format(row['Consistency'].values[0])
        # Add a dict (indent 4) of the discourse relations
        DR_results = {}
        for key in row.keys():
            if key not in ['taskcode', 'modelname', 'version', 'paraphrase', 'feature', 'Overall', 'Targeted', 'Counterfactual', 'Consistency']:
                DR_results[key] = row[key].values[0]
        for key in DR_results:
            verbalization += 'DiSQ Score for {}: {}\n'.format(key, DR_results[key])
        verbalization += '=== End of the results for model: {} ===\n'.format(self.modelname)

        # write the verbalization to a file, the file name is the modelname, and the dir is self.config.verbalization_dir
        fp = os.path.join(self.config.verbalization_dir, '{}.txt'.format(self.modelname))

        # if fp does not exist, then create it
        if not os.path.exists(fp):
            with open(fp, 'w') as f:
                f.write(verbalization)
        else:
            # if fp exists, then append the verbalization to it
            with open(fp, 'a') as f:
                f.write(verbalization)
        
        # load the verbalization file and print it
        with open(fp, 'r') as f:
            content = f.read()
        print(content)
        
        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluation.')
    parser.add_argument('--dataset', type=str, default='pdtb', help='Dataset: pdtb or ted')
    parser.add_argument('--modelname', type=str, default='13bchat', help='Model name: 13bchat, 13b, 7bchat, 7b, vicuna-13b')
    parser.add_argument('--modelurl', type=str, default=None, help='modelurl specific the models path in the hugging face model hub (for example, "meta-llama/Meta-Llama-3.1-8B"). modelurl has the right to overwrite modelname. If modelurl is provided, modelname will be ignored. It is used for new models that has not been specified in the config file.')
    parser.add_argument('--version', type=str, default='v1', help='Version of the dataset')
    parser.add_argument('--paraphrase', type=str, default=None, help='Paraphrase: p1, p2')
    parser.add_argument('--feature', type=str, default=None, help='Feature: None, or any feature')
    parser.add_argument('--hfpath', type=str, default='/mnt/data/yisong/hf-path', help='Huggingface path')
    parser.add_argument('--device_number', type=int, default=0, help='Device number')
    parser.add_argument('--verbalize', type=int, default=0, help='Whether to verbalize the results')
    args = parser.parse_args()
    
    config = DiSQ_Config(args.dataset, args.modelname, args.modelurl, args.version, args.paraphrase, args.feature, args.hfpath, args.device_number)
    NewEval = Eval(config, args.verbalize)
    NewEval.loop_through(desired_DR=None)
    NewEval.eval_all_level2_relations()
    NewEval.save_results()

    if args.verbalize == 1:
        NewEval.verbose()
    