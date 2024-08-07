import argparse
import os
import json


class QAUtils:
    # initialize the class
    def __init__(self):
        self.DR_description = {
            "Expansion.Conjunction": 'Expansion.Conjunction, it indicates that Arg1 and Arg2 make the same contribution with respect to that situation, or contribute to it together.',
            "Contingency.Cause.Reason": 'Contingency.Cause.Reason, it means when Arg1 gives the effect, while Arg2 gives its the reason, explanation or justification',
            "Expansion.Instantiation.Arg2-as-instance": 'Expansion.Instantiation.Arg2-as-instance, which means Arg2 provides one or more instances of the circumstances described by Arg1',
            "Comparison.Concession.Arg2-as-denier": "Comparison.Concession.Arg2-as-denier, which indicates that Arg2 denies or contradicts something in Arg1",
            "Expansion.Level-of-detail.Arg2-as-detail": "Expansion.Level-of-detail.Arg2-as-detail, which means Arg2 provides more detail about Arg1",
            "Temporal.Asynchronous.Precedence": "Temporal.Asynchronous.Precedence, which means the event described by Arg1 precedes that described by Arg2",
            "Expansion.Level-of-detail.Arg1-as-detail": "Expansion.Level-of-detail.Arg1-as-detail, which means Arg1 provides more detail about Arg2",
            "Expansion.Equivalence": "Expansion.Equivalence, which means when both arguments are taken to describe the same situation, but from diﬀerent perspectives",
            "Contingency.Cause.Result": "Contingency.Cause.Result, it means when Arg1 gives the reason, explanation or justification, while Arg2 gives its effect",
            "Contingency.Cause+Belief.Reason+Belief": "Contingency.Cause+Belief.Reason+Belief, which means evidence is provided to cause the hearer to believe",
            "Temporal.Synchronous": "Temporal.Synchronous, which means Arg1 and Arg2 are events that occur at the same time",
            "Expansion.Substitution.Arg2-as-subst": 'Expansion.Substitution.Arg2-as-subst, which means Arg2 conveys the alternative which is left after the situation associated with Arg1 is ruled out',
            "Temporal.Asynchronous.Succession": "Temporal.Asynchronous.Succession, is used when the event described by Arg2 precedes that described by Arg1",
            "Comparison.Concession.Arg1-as-denier": "Comparison.Concession.Arg1-as-denier, which indicates that Arg1 denies or contradicts something in Arg2",
            "Comparison.Contrast": "Comparison.Contrast means at least two differences between Arg1 and Arg2 are highlighted",
        }

        self.DR_eventR_mapping = {
            "Expansion.Conjunction": "Event1 and Event2 are contributed to the same situation",
            "Contingency.Cause.Reason": "Event2 is the reason for Event1",
            "Expansion.Instantiation.Arg2-as-instance": "Event2 is an instance of Event1",
            "Comparison.Concession.Arg2-as-denier": "Event2 denies or contradicts Event1",
            "Expansion.Level-of-detail.Arg2-as-detail": "Event2 provides more detail about Event1",
            "Temporal.Asynchronous.Precedence": "Event1 happens before Event2",
            "Expansion.Level-of-detail.Arg1-as-detail": "Event1 provides more detail about Event2",
            "Expansion.Equivalence": "Event1 and Event2 are equivalent",
            "Contingency.Cause.Result": "Event1 is the reason for Event2",
            "Contingency.Cause+Belief.Reason+Belief": "Event1 is the reason for Event2",
            "Temporal.Synchronous": "Event1 and Event2 happen at the same time",
            "Expansion.Substitution.Arg2-as-subst": "Event2 is an alternative to Event1",
            "Temporal.Asynchronous.Succession": "Event1 happens after Event2",
            "Comparison.Concession.Arg1-as-denier": "Event1 denies or contradicts Event2",
            "Comparison.Contrast": "Event1 and Event2 are contrasted",
        }

        self.DR_Q_mapping = {
            "Expansion.Conjunction":
            {
                'targeted': ['are contributed to the same situation'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with' , 'is reason for', 'is result of', 'is an example of'],
            },
            "Contingency.Cause.Reason":
            {
                'targeted': ['is reason for'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of', 'is equivalent to'],
            },
            "Expansion.Instantiation.Arg2-as-instance":
            {
                'targeted': ['is an example of'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Comparison.Concession.Arg2-as-denier":
            {
                'targeted': ['is denied or contradicted with'],
                'counterfactual': ['is reason for', 'is result of', 'is an example of', 'is equivalent to', 'does provide more detail about'],
            },
            "Expansion.Level-of-detail.Arg2-as-detail":
            {
                'targeted': ['does provide more detail about'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Temporal.Asynchronous.Precedence":
            {
                'targeted': ['does happens before'],
                'counterfactual': ['does happens after', 'is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of'],
            },
            "Expansion.Level-of-detail.Arg1-as-detail":
            {
                'targeted': ['does provide more detail about'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Expansion.Equivalence":
            {
                'targeted': ['is equivalent to'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is an example of'],
            },
            "Contingency.Cause.Result":
            {
                'targeted': ['is result of'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is an example of', 'is equivalent to'],
            },
            "Contingency.Cause+Belief.Reason+Belief":
            {
                'targeted': ['is reason for'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of', 'is equivalent to'],
            },
            "Temporal.Synchronous":
            {
                'targeted': ['does happens at the same time as'],
                'counterfactual': ['does happens before', 'is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of'],
            },
            "Expansion.Substitution.Arg2-as-subst":
            {
                'targeted': ['is an alternative to'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Expansion.Substitution.Arg1-as-subst":
            {
                'targeted': ['is an alternative to'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Temporal.Asynchronous.Succession":
            {
                'targeted': ['does happens after'],
                'counterfactual': ['does happens before', 'is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of'],
            },
            "Comparison.Concession.Arg1-as-denier":
            {
                'targeted': ['is denied or contradicted with'],
                'counterfactual': ['is reason for', 'is result of', 'is an example of', 'is equivalent to', 'does provide more detail about'],
            },
            "Comparison.Contrast":
            {
                'targeted': ['is contrasted with'],
                'counterfactual': ['is denied or contradicted with', 'is reason for', 'is result of', 'is an example of', 'is equivalent to'],
            },
        }

        self.converse_question_mapping = {
            # contingency
            'is result of': 'is reason for',
            'is reason for': 'is result of',
            # temporal
            'does happens at the same time as': 'does happens at the same time as',
            'does happens before': 'does happens after',
            'does happens after': 'does happens before',
            # comparison
            'is contrasted with': 'is contrasted with',
            'is denied or contradicted with': 'denies or contradicts with',
            # expansion
            'is an alternative to': 'is being provided an alternative by',
            'does provide more detail about': 'is being provided more detail by',
            'is equivalent to': 'is equivalent to',
            'are contributed to the same situation': 'are contributed to the same situation',
            'is an example of': 'is being exemplified by',
        }

        # Get the list for all keys in self.converse_question_mapping
        self.converse_question_list = list(self.converse_question_mapping.keys())

        self.DR_Q_mapping_index = {}
        for key, value in self.DR_Q_mapping.items():
            self.DR_Q_mapping_index[key] = {}
            for key2, value2 in value.items():
                self.DR_Q_mapping_index[key][key2] = [self.converse_question_list.index(item) for item in value2]
        print('self.DR_Q_mapping_index: ', self.DR_Q_mapping_index)
        # save it as a json file
        with open('data/DR_Q_mapping_index.json', 'w') as f:
            json.dump(self.DR_Q_mapping_index, f, indent=4)

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
        
        # Given all prompt in self.DR_Q_mapping, glue them into a grammarly correct question
        # all possible question is ['is result of', 'does happens at the same time as', 'is contrasted with', 'is an alternative to', 'is reason for', 'does provide more detail about', 'does happens before', 'is an example of', 'does happens after', 'is equivalent to', 'are contributed to the same situation', 'is denied or contradicted with']
        if prompt == 'is result of':
            return 'Is "{}" the result of "{}"?'.format(event1, event2)
        elif prompt == 'does happens at the same time as':
            return 'Does "{}" happen at the same time as "{}"?'.format(event1, event2)
        elif prompt == 'is contrasted with':
            return 'Is "{}" contrasted with "{}"?'.format(event1, event2)
        elif prompt == 'is an alternative to':
            return 'Is "{}" an alternative to "{}"?'.format(event1, event2)
        elif prompt == 'is reason for':
            return 'Is "{}" the reason for "{}"?'.format(event1, event2)
        elif prompt == 'does provide more detail about':
            return 'Does "{}" provide more detail about "{}"?'.format(event1, event2)
        elif prompt == 'does happens before':
            return 'Does "{}" happen before "{}"?'.format(event1, event2)
        elif prompt == 'is an example of':
            return 'Is "{}" an example of "{}"?'.format(event1, event2)
        elif prompt == 'does happens after':
            return 'Does "{}" happen after "{}"?'.format(event1, event2)
        elif prompt == 'is equivalent to':
            return 'Is "{}" equivalent to "{}"?'.format(event1, event2)
        elif prompt == 'are contributed to the same situation':
            return 'Is "{}" contributed to the same situation as "{}"?'.format(event1, event2)
        elif prompt == 'is denied or contradicted with':
            return 'Is "{}" denied or contradicted with "{}"?'.format(event1, event2)
        elif prompt == 'denies or contradicts with':
            return 'Does "{}" deny or contradict with "{}"?'.format(event1, event2)
        elif prompt == 'is being provided an alternative by':
            return 'Is "{}" being provided an alternative by "{}"?'.format(event1, event2)
        elif prompt == 'is being provided more detail by':
            return 'Is "{}" being provided more detail by "{}"?'.format(event1, event2)
        elif prompt == 'is being exemplified by':
            return 'Is "{}" being exemplified by "{}"?'.format(event1, event2)
        # put all question part into a list, e.g. "the result of", "happen at the same time as", "is contrasted with", "an alternative to", "the reason for", "provide more detail about", "happen before", "an example of", "happen after", "equivalent to", "contributed to the same situation", "denied or contradicted with"
        # question_prompt_list = ['the result of', 'happen at the same time as', 'contrasted with', 'an alternative to', 'the reason for', 'provide more detail about', 'happen before', 'an example of', 'happen after', 'equivalent to', 'contributed to the same situation', 'denied or contradicted with', 'deny or contradict with', 'being  an alternative by', 'being provided more detail by', 'being exemplified by']
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
    new_qa_utils = QAUtils()
    targeted_question, counterfactual_question, converse_targeted_question, converse_counterfactual_question = new_qa_utils.generate_questions('Event1', 'Event2', 'Comparison.Concession.Arg1-as-denier')
    print(targeted_question)
    print(counterfactual_question)
    print(converse_targeted_question)
    print(converse_counterfactual_question)
