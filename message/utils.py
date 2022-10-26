from message.models import BadWord
from django.core.cache import cache
import re


class FilterText:

    def __init__(self, input_text, force_update=False, regex='[\u064B-\u0652\u06D4\u0670\u0674\u06D5-\u06ED]+'):
        self.force_update = force_update
        self.input_text = input_text
        self._regex_compiler = re.compile(regex, re.UNICODE)

    @property
    def badword_list(self):
        qs = BadWord.objects.only('content').filter(active=True).values_list('content').distinct('content')
        retList = [item[0] for item in qs]
        return retList

    @property
    def badwords_key(self):
        return "badword_key_filter_list"

    def save_badwords_in_cache(self):
        badwords = self.badword_list
        cache.set(self.badwords_key, badwords)
        return badwords

    def get_badwords(self, force_update=False):
        if force_update or self.force_update:
            return self.save_badwords_in_cache()

        badwords = cache.get(self.badwords_key)
        if badwords is None:
            badwords = self.save_badwords_in_cache()
        return badwords

    def filter(self, text=None):

        if text is not None:
            self.input_text = text

        badwords = self.get_badwords()
        temp = self.input_text

        temp_list = str(temp).split(" ")
        return_list = []

        for word in temp_list:
            word_removed_special_chars = self.regex.sub('', word)
            if word_removed_special_chars in badwords:
                return_list.append(len(word) * "*")
            else:
                return_list.append(word)

        ret = " ".join(return_list)
        return ret

    @property
    def regex(self):
        return self._regex_compiler
