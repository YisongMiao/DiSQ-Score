import argparse
import os
import json


class QAUtils_P1:
    # initialize the class
    def __init__(self):
        self.converse_question_mapping = {
            # contingency
            'is the consequence of': 'is the cause of',
            'is the cause of': 'is the consequence of',
            # temporal
            'does occurs simultaneously as': 'does occurs simultaneously as',
            'does occurs before': 'does occurs after',
            'does occurs after': 'does occurs before',
            # comparison
            'is opposed to': 'is opposed to',
            'is negated by': 'negates',
            # expansion
            'serves as a substitute for': 'is being provided an substitute by',
            'provide additional information about': 'is being provided additional information by',
            'is equal to': 'is equal to',
            'are contributed to the same circumstance': 'are contributed to the same circumstance',
            'is an instance of': 'is being instantiated by',
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

        if prompt == 'serves as a substitute for':
            return 'Does "{}" serve as a substitute for "{}"?'.format(event1, event2)
        elif prompt == 'negates':
            return 'Does "{}" negate "{}"?'.format(event1, event2)
        elif prompt == 'is being instantiated by':
            return 'Is "{}" being instantiated by "{}"?'.format(event1, event2)
        elif prompt == 'does occurs before':
            return 'Does "{}" occur before "{}"?'.format(event1, event2)
        elif prompt == 'is opposed to':
            return 'Is "{}" opposed to "{}"?'.format(event1, event2)
        elif prompt == 'does occurs after':
            return 'Does "{}" occur after "{}"?'.format(event1, event2)
        elif prompt == 'is the consequence of':
            return 'Is "{}" the consequence of "{}"?'.format(event1, event2)
        elif prompt == 'is being provided an substitute by':
            return 'Is "{}" being provided an substitute by "{}"?'.format(event1, event2)
        elif prompt == 'is the cause of':
            return 'Is "{}" the cause of "{}"?'.format(event1, event2)
        elif prompt == 'are contributed to the same circumstance':
            return 'Are "{}" contributed to the same circumstance as "{}"?'.format(event1, event2)
        elif prompt == 'is an instance of':
            return 'Is "{}" an instance of "{}"?'.format(event1, event2)
        elif prompt == 'does occurs simultaneously as':
            return 'Does "{}" occur simultaneously as "{}"?'.format(event1, event2)
        elif prompt == 'provide additional information about':
            return 'Does "{}" provide additional information about "{}"?'.format(event1, event2)
        elif prompt == 'is negated by':
            return 'Is "{}" negated by "{}"?'.format(event1, event2)
        elif prompt == 'is equal to':
            return 'Is "{}" equal to "{}"?'.format(event1, event2)
        elif prompt == 'is being provided additional information by':
            return 'Is "{}" being provided additional information by "{}"?'.format(event1, event2)
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
    new_qa_utils = QAUtils_P1()
    targeted_question, counterfactual_question, converse_targeted_question, converse_counterfactual_question = new_qa_utils.generate_questions('Event1', 'Event2', 'Comparison.Concession.Arg1-as-denier')
    print(targeted_question)
    print(counterfactual_question)
    print(converse_targeted_question)
    print(converse_counterfactual_question)
