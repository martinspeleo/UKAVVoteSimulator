from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
import urllib2, hashlib
from avsimulation.models import Contest, Option, SimulationInput, SimulationInputAV
import settings
# Create your views here.

def form(request, postcode, con_name):
    con = Contest.objects.get(name = con_name)
    if "fptp" in request.POST.keys():
        hashed_ip = hashlib.sha224(settings.SECRET_KEY + 
                                   request.META["REMOTE_ADDR"]).hexdigest()
        hashed_postcode = hashlib.sha224(settings.SECRET_KEY + postcode).hexdigest()
        si = SimulationInput(hashed_ip = hashed_ip, 
                             hashed_postcode = hashed_postcode, 
                             fptp_vote = Option.objects.get(name=request.POST["fptp"],
                                                            contest=con))
        si.save()
        for option in con.option_set.all():
            if request.POST.has_key(option.name) and request.POST[option.name] != u"":
                siav = SimulationInputAV(simulation = si, 
                                         vote = option, 
                                         rank = int(request.POST[option.name]))
                siav.save()
        return HttpResponseRedirect(reverse(frontpage, args=[]))
    return render_to_response('form.html', 
                              {"postcode": postcode, 
                               "constituency": con},
                              context_instance = RequestContext(request))
																							
def frontpage(request):
    if "postcode" in request.GET.keys():
        postcode = request.GET["postcode"].replace(" ", "")
        try:
            req = urllib2.Request("http://mapit.mysociety.org/postcode/%s" % postcode)
            a=eval(urllib2.urlopen(req).read(), {"null": None})
            areas = [area 
                     for area 
                     in a["areas"].values() 
                     if area["type_name"] == 'UK Parliament constituency']
            con_name = areas[0]["name"]
            return HttpResponseRedirect(reverse(form, args=[postcode, con_name]))
        except urllib2.HTTPError:
            return render_to_response('main.html', 
                                      {"errormessage": "Could not find postcode", 
                                       "value": request.GET["postcode"]})
    return render_to_response('main.html')

def run_election(request):
    results = {}
    #Make Ballot Papers
    for contest in Contest.objects.all():
        ballots = [BallotPaper([option,], 
                               multiplicity = option.votes)
                   for option 
                   in contest.option_set.all()]
        results[contest] = (run_contest(contest, ballots))
    return render_to_response('results.html', 
                              {"results": results})

def add(x, y): return x + y
def and_(x, y): return x and y

def run_contest(contest, ballots):
    rounds = []
    options = list(contest.option_set.all())
    while len(options) > 1:
        ballots = [ballot for ballot in ballots if len(ballot.optionslist) > 0]
        count = [(option, 
                  reduce(add, 
                         [ballot.multiplicity 
                          for ballot 
                          in ballots 
                          if ballot.optionslist[0] == option],
                         0)
                  ) 
                 for option 
                 in options]
        count.sort(key=lambda a: a[1], reverse = True)
        rounds.append(count)
        loser = count[-1][0]
        options.remove(loser)
        for ballot in ballots:
            if loser in ballot.optionslist:
                ballot.optionslist.remove(loser)
    winner = options[0]
    return {"winner": winner, "rounds": rounds}
            
class BallotPaper:
    def __init__(self, optionslist, multiplicity = 1):
        #Check all options come from same contest.
        assert reduce(and_,
                      [option.contest == optionslist[0].contest
                       for option
                       in optionslist[1:]],
                      True)
        self.optionslist = optionslist
        self.multiplicity = multiplicity

