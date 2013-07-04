# coding: utf8
"""

Use Markov chains to generate random text that sounds Japanese.
This makes random pronounceable passwords that are both strong and easy
to memorize.
Of course English or any other language could be used in the sample text.
See more details at http://exyr.org/2011/random-pronounceable-passwords/
Author: Simon Sapin
License: BSD

Slightly adopted for Zato by adding more languages in addition to Japanese
and splitting the resulting string into dash-separated groups.

"""

from __future__ import division
import string
import itertools
import random
from collections import defaultdict

# Zato
from zato.common.util import grouper

# This is a romanization of the opening of "Genji Monogatari"
# by Murasaki Shikibu.
# Source: http://etext.lib.virginia.edu/japanese/genji/roman.html
japanese = '''
Idure no ohom-toki ni ka, nyougo, kaui amata saburahi tamahi keru naka ni,
ito yamgotonaki kiha ni ha ara nu ga, sugurete tokimeki tamahu ari keri.

Hazime yori ware ha to omohi agari tamahe ru ohom-kata-gata, mezamasiki mono ni
otosime sonemi tamahu. Onazi hodo, sore yori gerahu no kaui-tati ha, masite
yasukara zu. Asa-yuhu no miya-dukahe ni tuke te mo, hito no kokoro wo nomi
ugokasi, urami wo ohu tumori ni ya ari kem, ito atusiku nari yuki, mono kokoro-
boso-ge ni sato-gati naru wo, iyo-iyo aka zu ahare naru mono ni omohosi te hito
no sosiri wo mo e habakara se tamaha zu, yo no tamesi ni mo nari nu beki ohom-
motenasi nari.

Kamdatime, uhe-bito nado mo, ainaku me wo sobame tutu, "Ito mabayuki hito no
ohom-oboye nari. Morokosi ni mo, kakaru koto no okori ni koso, yo mo midare,
asikari kere" to, yau-yau amenosita ni mo adikinau, hito no mote-nayami-gusa ni
nari te, Yauki-hi no tamesi mo hiki ide tu beku nariyuku ni, ito hasitanaki koto
ohokare do, katazikenaki mi-kokoro-bahe no taguhi naki wo tanomi ni te mazirahi
tamahu.

TiTi no Dainagon ha nakunari te haha Kita-no-kata nam inisihe no yosi aru ni te,
oya uti-gusi, sasi-atari te yo no oboye hanayaka naru ohom-kata-gata ni mo itau
otora zu, nani-goto no gisiki wo mo motenasi tamahi kere do, tori-tate te haka-
bakasiki usiro-mi si nakere ba, koto aru toki ha, naho yori-dokoro naku kokoro-
boso-ge nari.


Saki no yo ni mo ohom-tigiri ya hukakari kem, yo ni naku kiyora naru tama no
wonoko miko sahe umare tamahi nu. Itusika to kokoro-motonagara se tamahi te,
isogi mawirase te go-ran-zuru ni, meduraka naru tigo no ohom-katati nari.

Iti-no-Miko ha, Udaizin no Nyougo no ohom-hara ni te, yose omoku, utagahi naki
Mauke-no-kimi to, yo ni mote-kasiduki kikoyure do, kono ohom-nihohi ni ha narabi
tamahu beku mo ara zari kere ba, ohokata no yamgotonaki ohom-omohi ni te, kono
Kimi wo ba, watakusi-mono ni omohosi kasiduki tamahu koto kagiri nasi.

Hazime yori osinabete no uhe-miya-dukahe si tamahu beki kiha ni ha ara zari ki.
Oboye ito yamgotonaku, zyauzu-mekasi kere do, warinaku matuhasa se tamahu amari
ni, sarubeki ohom-asobi no wori-wori, nani-goto ni mo yuwe aru koto no husi-busi
ni ha, madu mau-nobora se tamahu. Aru-toki ni ha ohotono-gomori sugusi te,
yagate saburahase tamahi nado, anagati ni o-mahe sara zu mote-nasa se tamahi si
hodo ni, onodukara karoki kata ni mo miye si wo, kono Miko umare tamahi te noti
ha, ito kokoro koto ni omohosi oki te tare ba, Bau ni mo, you se zu ha, kono
Miko no wi tamahu beki na'meri to, Ichi-no-Miko no Nyougo ha obosi utagahe ri.
Hito yori saki ni mawiri tamahi te, yamgotonaki ohom-omohi nabete nara zu, Miko-
tati nado mo ohasimase ba, kono Ohom-kata no ohom-isame wo nomi zo, naho
wadurahasiu kokoro-gurusiu omohi kikoye sase tamahi keru.
Kasikoki mi-kage wo ba tanomi kikoye nagara, otosime kizu wo motome tamahu hito
ha ohoku, waga mi ha ka-yowaku mono-hakanaki arisama ni te, naka-naka naru mono-
omohi wo zo si tamahu. Mi-tubone ha Kiritubo nari. Amata no ohom-Kata-gata wo
sugi sase tamahi te, hima naki o-mahe-watari ni, hito no mi-kokoro wo tukusi
tamahu mo, geni kotowari to miye tari. Mau-nobori tamahu ni mo, amari uti-sikiru
wori-wori ha, uti-hasi, wata-dono no koko kasiko no miti ni, ayasiki waza wo si
tutu, ohom-okuri mukahe no hito no kinu no suso, tahe gataku, masanaki koto mo
ari. Mata aru toki ni ha, e sara nu me-dau no to wo sasi-kome, konata kanata
kokoro wo ahase te, hasitaname wadurahase tamahu toki mo ohokari. Koto ni hure
te kazu sira zu kurusiki koto nomi masare ba, ito itau omohi wabi taru wo, itodo
ahare to go-ran-zi te, Kourau-den ni motoyori saburahi tamahu Kaui no zausi wo
hoka ni utusa se tamahi te, Uhe-tubone ni tamaha su. Sono urami masite yara m
kata nasi.
'''

# http://www.gutenberg.org/files/17544/17544-0.txt
occitan = """
  Despen lou ben per compas é mesure,
E mesquemés lou que tas amassat:
Que puch aprés si lou tas despensat,
Den gaigna mes aquo ba a labenture.


    XVI.

  Tant quom te sab force argent en la bousse
De toutis es Moussur é coumpaignon
Quan nou nas més delechat és deu mon,
Coum si jamés connegut nou t’augousse.


    XVII.

  Dits la paraule aprés lauë pensade
A gens segrets que namen pas lou brut:
Atau ne ba deu perpaus quas tengut,
Coume deu bent ou duë peire getade.


    XVIII.

  Si hés plase helou de boun couratge,
Sapies aqui, gouerdet de tempacha,
Que nou te caille à la fin reproucha,
Qu’eu regast pert, é l’amic, é lou gatge.


    XIX.

  Si bos auë peus bounis locs l’entrade,
Saget de hé coume beses que hen,
Nou sies fachous, ny broutous, ni bilén,
Ni lampourné, coume bere mainade.


    XX.

  Si ta bertut force de ben s’amasse,
Parens caitious bergoine nou te hén:
Qu’et beau mesleu que lou darré bilen,
Este prumé gentilhomme en sa race.


    XXI.

  A tribailla hé tout se que tu pousques
Esburbe-te per tout de la doun és:
Praube mestié que i d’vn truque taulés,
D’vn pan derdut, enjourrit, bade mousques.


    XXII.

  Nou hiques pas en ta grane coulére
Que tu madich nout pousques matiga:
Aquet que sab soun bici castiga,
Per dessus touts lo u plus sage s’apere


    XXIII.

  Quan as lou temps de poude hé la cause,
Nac boutes pas à tantos ou douman,
Qui per vn cop d’agine de la man,
N’abigne plus ni lou temps, n’i la pause.


    XXIV.

  Nou t’anes pas cargua de fantasies,
Mes tot gaujous agerge tous quehés:
Nou darés ourdes à cinq targes dahés:
A mil escuts de tas malencounies.


    XXV.

  Aule escourga sadits om hé la couë
De loungs ahés, charges, é coussoulats:
La populasse aporte tant de caps,
Que mes escoute, oun mes om l’arrasouë.


    XXVI.

  Las sages nou disen pas en bades,
Hemne que bo tant de joies pourta,
Si sous mouiens nac poden supourta,
Ou be hé mau, ou he pourte las brages.


    XXVII.

  Tut troũpes plan mes souuen se t’uesperes
De toun parent, ben, ou coumoditat,
Tu sabes trop sac as esprimentat,
Que males son de ton hust las esteres,


    XXVIII.

  Nou hasses mau d’aqueste, ou daute sorte,
Pensan qu’aprés degun nac sabera,
Tu nou pouïres tant lou houec capera,
Q’a la perfin la humade nou sorte.


    XXIX.

  Si toun prouheit d’entreprene t’assajes,
Nou creignes pas aquets que nan despieit,
Ni l’embejous, que name toun prouheit,
Que pan é bin, sapere tu ten ajes.


    XXX.

  Nou sies daquets qu’espousaran vë More,
Vn arrebrec, mes qu’age force argent.
Si nas mouillé de quauque boune gent;
L’argent s’en ba, é la bestio demoro.


    XXXI.

  D’ome trichot, jogue tout, encoublaire,
Nou hasses pas amic, é coumpaignoun,
Puch quet nou biu que de troũpa lou moun,
De t’aguerri, nou s’endare pas gouaire.


    XXXII.

  Si nou las heit, nous bantes de l’oubratje,
Ni d’autru ben nou prenges la banson,
Ou descridat seras per tout lou moun,
Lairon d’aunou, que nes pas petit gatje.
"""

breton = """
.NHO
40           MEULEUDI SANTEZ ANNA
.NTO

  Va Breudeur ker, ne laeromp ket loden an Aotrou
Doue. Hen dreist pep tra, eo hen deuz great ar Verc'hez
Sakr ar pez ma zeo. Eva, ar genta maouez, a gollas ar
bed : Eur verc'h da Eva eo a dle hen savetei. Ha Doue
a bell, a bourchassas, a aozas pep tra evit kas da benn
ar pez hen doa rezolvet dre druez ouzomp.
  Mez ma reaz evit ober euz ar Verc'hez eur grouadurez
ker pur, burzud var burzud, Santez Anna a reas he lod.
  1° Sellit outhi : He merc'h c'hoas iaouankik flamm,
a zo en he c'hichen o teski lezen Doue.
  2° D'an eil Santez Anna n'he doa krouadur ebet
nemet-hi. Ha koulskoude, d'an oad a dri bloas, Mari a
zo kaset d'an templ ha roet da Zoue.
  Tadou ha mammou, setu aze ho skouer. Peurvuia
eur c'hrouadur a vez ar pez ma vez great : nebeut a
drec'h wen. En em glemm a rear euz ar vugale ; guel-
loc'h e ve en em glemm euz ar re nebeut a zoursi a vez
bet kemeret d'ho c'helen ervad.
  Eürus an nep er bed-ma, a ra evit Doue, evit he
nesa, evithan he unan, ar pez a c'houlenn mad an ene.
  Koulskoude, hag e tiguesfe ganheomp, kueza er
pec'het, ne gollomp ket a fizians.
  Eur sant hen deus bet lavaret divar benn ar Verc'hes :
omnipotentia supplex. Me 'lavaro da m'zro, Santez
Anna dre he feden a zeuio a benn euz kement e dezho
c'hoant. Ar Verc'hez a zo he merc'h, Jesus-Krist a zo
he mab bihan : Galloud he deuz eta dirag Doue. Ha
hent all, ne c'hello ket mankout a garantez evidomp
ni bugale ar beg douar ma a zo en em wlestet dezhi.

.NHO
         MEULEUDI SANTEZ ANNA                 41
.NTO

En em erbedomp eta outhi gant fizians. Mar d'homp
mad, hi hor jikouro da genderc'hel ; mar bevomp er
pec'het, hi a astenno d'heomp he dourn evit hor zevel
da genta ha rei d'heomp nerz da jomm en hor zao beteg
ar fin.
                                             AMEN.

.NPO
"""

def pairwise(iterable):
    """
Yield pairs of consecutive elements in iterable.
>>> list(pairwise('abcd'))
[('a', 'b'), ('b', 'c'), ('c', 'd')]
"""
    iterator = iter(iterable)
    try:
        a = iterator.next()
    except StopIteration:
        return
    for b in iterator:
        yield a, b
        a = b
        
class MarkovChain(object):
    """
If a system transits from a state to another and the next state depends
only on the current state and not the past, it is said to be a Markov chain.
It is determined by the probability of each next state from any current
state.
See http://en.wikipedia.org/wiki/Markov_chain
The probabilities are built from the frequencies in the `sample` chain.
Elements of the sample that are not a valid state are ignored.
"""
    def __init__(self, sample):
        self.counts = counts = defaultdict(lambda: defaultdict(int))
        for current, next in pairwise(sample):
            counts[current][next] += 1
        
        self.totals = dict(
            (current, sum(next_counts.itervalues()))
            for current, next_counts in counts.iteritems()
        )
        
    def next(self, state):
        """
Choose at random and return a next state from a current state,
according to the probabilities for this chain
"""
        nexts = self.counts[state].iteritems()
        # Like random.choice() but with a different weight for each element
        rand = random.randrange(0, self.totals[state])
        # Using bisection here could be faster, but simplicity prevailed.
        # (Also it’s not that slow with 26 states or so.)
        for next_state, weight in nexts:
            if rand < weight:
                return next_state
            rand -= weight
    
    def __iter__(self):
        """
Return an infinite iterator of states.
"""
        state = random.choice(self.counts.keys())
        while True:
            state = self.next(state)
            yield state

def generate_password(length=16):
    chain = MarkovChain(
        c for c in japanese.lower() + occitan.lower() + breton.lower() if c in string.ascii_lowercase
    )
    return '-'.join(''.join(elems) for elems in (grouper(4, ''.join(itertools.islice(chain, length)))))
