import argparse
import os
import json


class QAUtils_P2:
    # initialize the class
    def __init__(self):
        self.converse_question_mapping = {
            # contingency
            'is due to': 'leads to',
            'leads to': 'is due to',
            # temporal
            'takes place simultaneously as': 'takes place simultaneously as',
            'does takes place before': 'does takes place after',
            'does takes place after': 'does takes place before',
            # comparison
            'is contrary to': 'is contrary to',
            'is refuted by': 'refutes',
            # expansion
            'acts as a replacement for': 'is replaced by',
            'present more specifics on': 'is presented with more specifics by',
            'is on par with': 'is on par with',
            'are contributed to the same scenario': 'are contributed to the same scenario',
            'serves as an example of': 'is exemplified by'
        }

        map_fp = 'data/DR_Q_mapping_index.json'
        with open(map_fp, 'r') as f:
            self.DR_Q_mapping_index = json.load(f)
        
        # Get the list for all keys in self.converse_question_mapping
        self.converse_question_list = list(self.converse_question_mapping.keys())

        # Consilidate all keys and values in self.converse_question_mapping and put them into a list
        self.all_prompts = []
        for key, value in self.converse_question_mapping.items():
            self.all_prompts.append(key)
            self.all_prompts.append(value)
        # remove the duplicates
        self.all_prompts = list(set(self.all_prompts))
        print('self.all_prompts: ', self.all_prompts)

        # Transform the index to the actual DR, 
        self.DR_Q_mapping = {}
        for key, value in self.DR_Q_mapping_index.items():
            self.DR_Q_mapping[key] = {
                'targeted': [self.converse_question_list[item] for item in value['targeted']],
                'counterfactual': [self.converse_question_list[item] for item in value['counterfactual']]
            }
        
        # print in json format with indent 4
        print(json.dumps(self.DR_Q_mapping, indent=4))

        # print the number of targeted questions and counterfactual questions for each DR
        for key, value in self.DR_Q_mapping.items():
            print(key, len(value['targeted']), len(value['counterfactual']))

        # consilidate the DR_Q_mapping into a list of questions
        self.DR_Q_list = []
        for key, value in self.DR_Q_mapping.items():
            for key2, value2 in value.items():
                for item in value2:
                    self.DR_Q_list.append(item)
        # remove the duplicates
        self.DR_Q_list = list(set(self.DR_Q_list))
        print('self.DR_Q_list: ', self.DR_Q_list)

        # assert that every question in self.DR_Q_list is in self.converse_question_mapping
        for item in self.DR_Q_list:
            assert item in self.converse_question_mapping.keys()
        print('assertion passed')


    def glue(self, event1, event2, prompt):
        event1 = event1.lower() + ' (event 1)'
        event2 = event2.lower() + ' (event 2)'
        
        if prompt == 'takes place simultaneously as':
            return 'Does "{}" take place simultaneously as "{}"?'.format(event1, event2)
        elif prompt == 'is contrary to':
            return 'Is "{}" contrary to "{}"?'.format(event1, event2)
        elif prompt == 'is replaced by':
            return 'Is "{}" replaced by "{}"?'.format(event1, event2)
        elif prompt == 'present more specifics on':
            return 'Does "{}" present more specifics on "{}"?'.format(event1, event2)
        elif prompt == 'is on par with':
            return 'Is "{}" on par with "{}"?'.format(event1, event2)
        elif prompt == 'does takes place before':
            return 'Does "{}" take place before "{}"?'.format(event1, event2)
        elif prompt == 'is exemplified by':
            return 'Is "{}" exemplified by "{}"?'.format(event1, event2)
        elif prompt == 'is due to':
            return 'Is "{}" due to "{}"?'.format(event1, event2)
        elif prompt == 'leads to':
            return 'Does "{}" lead to "{}"?'.format(event1, event2)
        elif prompt == 'is refuted by':
            return 'Is "{}" refuted by "{}"?'.format(event1, event2)
        elif prompt == 'are contributed to the same scenario':
            return 'Are "{}" contributed to the same scenario as "{}"?'.format(event1, event2)
        elif prompt == 'acts as a replacement for':
            return 'Does "{}" act as a replacement for "{}"?'.format(event1, event2)
        elif prompt == 'refutes':
            return 'Does "{}" refute "{}"?'.format(event1, event2)
        elif prompt == 'is presented with more specifics by':
            return 'Is "{}" presented with more specifics by "{}"?'.format(event1, event2)
        elif prompt == 'does takes place after':
            return 'Does "{}" take place after "{}"?'.format(event1, event2)
        elif prompt == 'serves as an example of':
            return 'Does "{}" serve as an example of "{}"?'.format(event1, event2)
        else:
            return 'Error: prompt not found'
        
    def generate_questions(self, event1, event2, DR):
        # Get both targeted and counterfactual questions for a given DR
        # return a list of questions
        tatgeted_question_prompts = self.DR_Q_mapping[DR]['targeted']
        counterfactual_questions = self.DR_Q_mapping[DR]['counterfactual']
        # The order of event1 and event2 is important. 
        # In forward_relations, it is event1 is X to event2
        
        forward_relations = ["Temporal.Asynchronous.Precedence", "Expansion.Level-of-detail.Arg1-as-detail", "Comparison.Concession.Arg1-as-denier"]

        if DR in forward_relations:
            targeted_question = self.glue(event1, event2, tatgeted_question_prompts[0])
            counterfactual_question = [self.glue(event1, event2, item) for item in counterfactual_questions]
            converse_targeted_question = self.glue(event2, event1, self.converse_question_mapping[tatgeted_question_prompts[0]])
            converse_counterfactual_question = [self.glue(event2, event1, self.converse_question_mapping[item]) for item in counterfactual_questions]
        else:
            # 
            targeted_question = self.glue(event2, event1, tatgeted_question_prompts[0])
            counterfactual_question = [self.glue(event2, event1, item) for item in counterfactual_questions]
            # then we need to generate the converse question for both targeted and counterfactual questions, which means we alter the order of event1 and event2 but use a converse prompt
            converse_targeted_question = self.glue(event1, event2, self.converse_question_mapping[tatgeted_question_prompts[0]])
            converse_counterfactual_question = [self.glue(event1, event2, self.converse_question_mapping[item]) for item in counterfactual_questions]
        
        return targeted_question, counterfactual_question, converse_targeted_question, converse_counterfactual_question


if __name__ == '__main__':
    new_qa_utils = QAUtils_P2()
    targeted_question, counterfactual_question, converse_targeted_question, converse_counterfactual_question = new_qa_utils.generate_questions('Event1', 'Event2', 'Comparison.Concession.Arg1-as-denier')
    print(targeted_question)
    print(counterfactual_question)
    print(converse_targeted_question)
    print(converse_counterfactual_question)
