from message.models import BadWord
from django.core.cache import cache
import re


class FilterText:

    def __init__(self, input_text, force_update=False):
        self.force_update = force_update
        self.input_text = input_text

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
        for badword in badwords:
            temp = re.sub(badword, len(badword)*"*", temp)
        return temp
