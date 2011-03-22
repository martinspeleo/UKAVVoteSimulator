from django.db import models

class Contest(models.Model):
    #constituency_id =  models.CharField(max_length=100)
    name =  models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.name)

class Party(models.Model):
    name =  models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.name)
    
class Option(models.Model):
    contest = models.ForeignKey(Contest)
    party =  models.ForeignKey(Party)
    name =  models.CharField(max_length=100)
    votes = models.IntegerField()

    def __unicode__(self):
        return u"%s (%s)" % (unicode(self.name), unicode(self.contest.name))

class SimulationInput(models.Model):
    hashed_ip = models.CharField(max_length=56)
    hashed_postcode = models.CharField(max_length=56)
    fptp_vote = models.ForeignKey(Option)

class SimulationInputAV(models.Model):
    simulation = models.ForeignKey(SimulationInput)
    vote = models.ForeignKey(Option)
    rank = models.IntegerField()
