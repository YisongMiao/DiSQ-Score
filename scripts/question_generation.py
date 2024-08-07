import json
import argparse
import os
import json
from collections import defaultdict

from disq_config import DiSQ_Config


class QG:
  # initialize the class
  def __init__(self, dataset, modelname, version, paraphrase, feature, config):
    self.dataset = dataset
    self.modelname = modelname
    self.version = version
    self.paraphrase = paraphrase
    self.feature = feature
    self.config = config
    
    self.QAUtils = self.config.QAUtils
    self.data_dict = self.config.data_dict
    
  def loop_through(self):
    self.output_dict = defaultdict(dict)
    print('length of data_dict:', len(self.data_dict)) 

    self.question_dict = dict()
    for instance_key, current_instance in self.data_dict.items():
      events = current_instance['events']
      DR = current_instance['DR']
      conn = current_instance['Conn']
      arg1 = current_instance['arg1']
      arg2 = current_instance['arg2']
      if self.dataset == 'pdtb':
        context = current_instance['context']

      if self.feature == 'conn':
        arg2 = ', {}, {}'.format(conn, arg2)

      self.question_dict[instance_key] = dict()
      for pair_idx, event_pair in enumerate(events):
        event1 = event_pair[0]
        event2 = event_pair[1]
        targeted_question, counterfactual_question, converse_targeted_question, converse_counterfactual_question = self.QAUtils.generate_questions(event1, event2, DR)

        questions = {
            'targeted_question': [targeted_question],
            'counterfactual_question': counterfactual_question,
            'converse_targeted_question': [converse_targeted_question],
            'converse_counterfactual_question': converse_counterfactual_question
          }

        header = "Respond to a true-or-false question that is derived from a two-sentence discourse. This discourse consists of Sentence 1 (Sent1) and Sentence 2 (Sent2), linked by a specific type of relationship such as causal, temporal, expansion, contrasting, etc. The question will focus on two events mentioned within this discourse. Your task is to determine if these events exhibit the specific relationship highlighted in the question. Please provide a 'True' or 'False' answer based on this analysis.\n\n"

        if self.feature != 'context':  # This is the usual case, where we do not need to add the context.
          header += 'Sent1: "{}". Sent2: "{}".\nQuestion: '.format(arg1, arg2)
        else:
          header += 'Context: "{}"\n\nSent1: "{}". Sent2: "{}".\n\nQuestion: '.format(context, arg1, arg2)

        if self.version == 'v1':
          for key in questions:
            for idx_, item in enumerate(questions[key]):
              if self.feature == 'context':
                item += ' Please answer the question by referring to the context.'
              item += ' True or False?'
              questions[key][idx_] = header + item + '\nAnswer: '
        if self.version == 'v2':
          for key in questions:
            for idx_, item in enumerate(questions[key]):
              # The purpose is to remove the impact of keywords "True" / "False" in the question.
              # header = "Respond to a true-or-false question that is derived from a two-sentence discourse. This discourse consists of Sentence 1 (Sent1) and Sentence 2 (Sent2), linked by a specific type of relationship such as causal, temporal, expansion, contrasting, etc. The question will focus on two events mentioned within this discourse. Your task is to determine if these events exhibit the specific relationship highlighted in the question. \n\n"
              if self.feature == 'context':
                header = 'Respond to a true-or-false question that is derived from a two-sentence discourse. This discourse consists of Sentence 1 (Sent1) and Sentence 2 (Sent2), linked by a specific type of relationship such as causal, temporal, expansion, contrasting, etc. The question will focus on two events mentioned within this discourse. Your task is to determine if these events exhibit the specific relationship highlighted in the question.\n\nContext: "{}"\n\nSent1: "{}". Sent2: "{}".\n\nQuestion: '.format(context, arg1, arg2)
                item += ' Please answer the question by referring to the context.'
              else:
                header = 'Respond to a true-or-false question that is derived from a two-sentence discourse. This discourse consists of Sentence 1 (Sent1) and Sentence 2 (Sent2), linked by a specific type of relationship such as causal, temporal, expansion, contrasting, etc. The question will focus on two events mentioned within this discourse. Your task is to determine if these events exhibit the specific relationship highlighted in the question. \n\nSent1: "{}". Sent2: "{}".\nQuestion: '.format(arg1, arg2)
              questions[key][idx_] = header + item + '\nAnswer: '
        if self.version == 'v3':
          for key in questions:
            for idx_, item in enumerate(questions[key]):
              if self.feature == 'context':
                item += ' Please answer the question by referring to the context.'
              item += ' True or False?'
              questions[key][idx_] = header + item + '\nAnswer:\n'
        if self.version == 'v4':
          for key in questions:
            for idx_, item in enumerate(questions[key]):
              if self.feature == 'context':
                item += ' Please answer the question by referring to the context.'
              item += ' True or False?'
              questions[key][idx_] = header + item + ' Answer: '
        
        self.question_dict[instance_key][pair_idx] = questions
    
    # Dump the question_dict to a JSON file
    # fp is the self.config.question_dir and necessary information from self.config.taskname
    fp = os.path.join(self.config.question_dir, '{}.json'.format(self.config.taskname))
    with open(fp, 'w') as f:
        json.dump(self.question_dict, f, indent=4)


if __name__ == '__main__':
    print('Start')

    parser = argparse.ArgumentParser()
    # model name
    parser.add_argument('--dataset', type=str, default='pdtb', help='pdtb or ted?')
    parser.add_argument('--modelname', type=str, default=None, help='None (does not care which modle we deal with), only applicable for using historical QA: 13b, 13bchat, vicuna.')
    parser.add_argument('--version', type=str, default='v1', help='v1, v2, v3, or v4?')
    parser.add_argument('--paraphrase', type=str, default=None, help='Options: None (default), p1, or p2 (paraphrasing to our original questions)')
    parser.add_argument('--feature', type=str, default=None, help='Options: conn, context, or history. Due to dataset characteristics, conn and context are only applicable to PDTB.')

    p = parser.parse_args()

    # Create a new config file    
    new_disq_config = DiSQ_Config(dataset=p.dataset, modelname=p.modelname, modelurl=None, version=p.version, paraphrase=p.paraphrase, feature=p.feature, hfpath=None, device_number=None)

    qg = QG(p.dataset, p.modelname, p.version, p.paraphrase, p.feature, new_disq_config)
    qg.loop_through()
