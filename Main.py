import os
import cv2

import math
import numpy as np

from PIL import Image
from PIL import ImageDraw

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog

from matplotlib import colors
import matplotlib.image as img
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D

from scipy.stats import zscore
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

saveFilename = None


def capture():
    global rlable

    cap = cv2.VideoCapture(0)

    roi_selected = False
    i_dist = []

    while True:
        ret, frame = cap.read()
        k = cv2.waitKey(1)

        if k & 0xFF == ord("s") and roi_selected:
            shape = cropped.shape
            r_dist, g_dist, b_dist, i_dist = [], [], [], []
            for i in range(shape[1]):
                r_val = np.mean(cropped[:, i][:, 0])
                g_val = np.mean(cropped[:, i][:, 1])
                b_val = np.mean(cropped[:, i][:, 2])
                i_val = (r_val + g_val + b_val) / 3

                r_dist.append(r_val)
                g_dist.append(g_val)
                b_dist.append(b_val)
                i_dist.append(i_val)

            break

        elif k & 0xFF == ord("r"):
            r = cv2.selectROI("Select ROI", frame)
            roi_selected = True
            cropped = frame[int(r[1]) : int(r[1] + r[3]), int(r[0]) : int(r[0] + r[2])]
            cv2.imshow("Selected ROI", cropped)

        elif k & 0xFF == ord("q"):

            print("[ ? ] Exit Without Saving ?")

            i_dist = []
            break

        if not roi_selected:
            cv2.imshow("Frame", frame)

    cap.release()
    cv2.destroyAllWindows()

    return i_dist


def normalise(spectrumIn):
    spectrumOut = []

    maxPoint = max(spectrumIn)

    for value in spectrumIn:
        spectrumOut.append(value / maxPoint)

    return spectrumOut


def reflectance(reference, sample):

    reflectance = []

    for i in range(len(sample)):
        if sample[i] == 0:
            reflectance.append(0)
        else:
            reflectance.append(
                1
                - (sample[i] / reference[i])
                + (-math.log(sample[i] / reference[i], 10) / 5)
            )

    return reflectance


def absorbance(reference, sample):

    absorbance = []

    for i in range(len(sample)):
        if sample[i] == 0:
            absorbance.append(0)
        else:
            absorbance.append(-math.log(sample[i] / reference[i], 10) / 5)

    return absorbance


def transmittance(reference, sample):

    transmittance = []

    for i in range(len(sample)):
        if sample[i] == 0:
            transmittance.append(0)
        else:
            transmittance.append(sample[i] / reference[i])

    return transmittance


pixel = [115, 146, 193, 250, 312, 329, 404]
wavelength = [405.4, 436.6, 487.7, 546.5, 611.6, 631.1, 708]
reference = [
    0.022867116398281522,
    0.022867116398281522,
    0.01939870834350586,
    0.019590424961513943,
    0.019015266100565593,
    0.015285412470499674,
    0.012993472483423021,
    0.010736390948295593,
    0.009751642710632748,
    0.010649246672789256,
    0.011555566953288186,
    0.014143802656067744,
    0.017620927890141806,
    0.018100232283274332,
    0.017176488902833728,
    0.013673213455412123,
    0.011398699482282003,
    0.010849680569436816,
    0.010379093289375306,
    0.010431379278500874,
    0.010318091478612687,
    0.010675388740168677,
    0.0105359575814671,
    0.011442275775803458,
    0.010631819069385528,
    0.010466241472297244,
    0.010535958376195698,
    0.011111123065153758,
    0.011503279805183411,
    0.010413953496350182,
    0.009847502741548749,
    0.00895861311091317,
    0.009446631438202327,
    0.010239663687017229,
    0.010727679398324754,
    0.010065367817878723,
    0.00874074849817488,
    0.007939004566934372,
    0.007572991251945496,
    0.008008721073468526,
    0.008226583600044251,
    0.00813072317176395,
    0.0077124225431018404,
    0.007407412065400018,
    0.00753813087940216,
    0.007651419970724317,
    0.00788671460416582,
    0.00787799961037106,
    0.007459699511528015,
    0.007834428879949782,
    0.007764711942937638,
    0.008662316468026903,
    0.010204802287949457,
    0.011102408236927456,
    0.0119041512409846,
    0.012000010212262472,
    0.01119826528761122,
    0.010387807753350999,
    0.01058824168311225,
    0.00940305405192905,
    0.009525061183505587,
    0.009830071263843112,
    0.008775604565938315,
    0.009167762200037639,
    0.008087151447931925,
    0.008444450563854641,
    0.008854037589497037,
    0.009664496580759685,
    0.010901969803704156,
    0.011067546208699543,
    0.010753819942474365,
    0.009472776452700298,
    0.009124190078841316,
    0.008705889450179206,
    0.009176478054788377,
    0.008801750540733337,
    0.008758176962534588,
    0.008697173827224307,
    0.009193906585375467,
    0.01068410376707713,
    0.011337698830498592,
    0.01037909123632643,
    0.007755996684233347,
    0.006788675685723622,
    0.006239655299319161,
    0.006893250164058474,
    0.007677565481927659,
    0.008296302623218961,
    0.009647066858079699,
    0.009925932751761542,
    0.011215695142745973,
    0.011625281439887154,
    0.012505455546908907,
    0.012130728430218167,
    0.012993472682105172,
    0.013141621748606364,
    0.013673210806316801,
    0.014422665039698282,
    0.015721142954296535,
    0.017455348968505858,
    0.020165592034657797,
    0.01874511374367608,
    0.020967338614993627,
    0.02092376033465068,
    0.026466248830159505,
    0.028305029604170057,
    0.031965161561965945,
    0.029943370752864417,
    0.02978651636176639,
    0.03051853398482005,
    0.03298476523823208,
    0.036671025620566476,
    0.04034858730104235,
    0.039747274319330846,
    0.042074082295099895,
    0.042875825961430865,
    0.04572551396158007,
    0.04568193541632758,
    0.0479303134812249,
    0.047808316151301065,
    0.05173858867751228,
    0.053777796162499315,
    0.06027014209164513,
    0.05962526222070058,
    0.0648540114197466,
    0.06301523461937904,
    0.06459257285628055,
    0.06708495260940657,
    0.06901957968870799,
    0.07255768789185418,
    0.07761218229929606,
    0.07800435145696004,
    0.08119393640094334,
    0.08013945486810473,
    0.0801917568180296,
    0.07960787342654334,
    0.08067107021808624,
    0.08181269082758162,
    0.08539441128571829,
    0.08740749571058486,
    0.0907887593905131,
    0.09135521385404799,
    0.09357742402288649,
    0.09327241275045607,
    0.09505015307002597,
    0.09435299025641547,
    0.09618302583694459,
    0.09619173275099861,
    0.09928539858924017,
    0.10262307087580363,
    0.11002173741658529,
    0.11311540179782444,
    0.11932886918385825,
    0.1180478188726637,
    0.120287477572759,
    0.11996504081620112,
    0.11993894471062554,
    0.12140299240748087,
    0.12344220108456083,
    0.12506311469607884,
    0.12768619590335423,
    0.12795633686913385,
    0.1292635276582506,
    0.13228748798370363,
    0.13716765456729466,
    0.14238767623901366,
    0.14854891671074763,
    0.15338552792867025,
    0.15586055437723798,
    0.15850982348124185,
    0.15809153980678983,
    0.16162099520365397,
    0.16304140620761448,
    0.16866240395439994,
    0.17212214787801106,
    0.17682810571458604,
    0.17704586982727052,
    0.18061022758483888,
    0.1797037304772271,
    0.18371248457166886,
    0.18440962314605713,
    0.18658827251858182,
    0.185089381535848,
    0.18752947807312012,
    0.18945541063944496,
    0.1963748582204183,
    0.20020052274068198,
    0.20396530363294815,
    0.20455789777967667,
    0.2068672858344184,
    0.20787817478179935,
    0.21059717390272356,
    0.21069304360283744,
    0.2136473242441813,
    0.21068422317504884,
    0.21518099043104386,
    0.21249666849772134,
    0.21792583995395234,
    0.2145793925391303,
    0.21934625413682726,
    0.21114578353034127,
    0.2160433684455024,
    0.21131131119198268,
    0.22176884015401208,
    0.2232590240902371,
    0.2338036542468601,
    0.23067546049753826,
    0.23776917033725317,
    0.2337953315840827,
    0.24321577231089275,
    0.24059272925058997,
    0.24934212976031833,
    0.2479390589396159,
    0.25959038151635067,
    0.2590238881111145,
    0.2664487054612901,
    0.2620652514033847,
    0.26686699443393286,
    0.26273610803816055,
    0.26873177316453717,
    0.2653330394956801,
    0.2714159189330207,
    0.2675205712848239,
    0.27426565753089055,
    0.2751806338628133,
    0.28237883991665313,
    0.2832415866851807,
    0.28906292385525173,
    0.28521099567413327,
    0.29204319424099395,
    0.2901175324122111,
    0.2979433970981174,
    0.2992771291732788,
    0.3025799613528781,
    0.30175210846794975,
    0.3028763177659776,
    0.30036650127834746,
    0.3000614823235406,
    0.2982662826114231,
    0.2987804349263509,
    0.29749066140916613,
    0.2981268241670397,
    0.29517254723442926,
    0.2971333376566569,
    0.2961921339564853,
    0.2992509402169122,
    0.29991326385074196,
    0.30179560634824965,
    0.3029546263482836,
    0.3053250000211927,
    0.30501125812530516,
    0.3067018773820665,
    0.30562127113342286,
    0.30549926651848686,
    0.3063271453645494,
    0.30556898011101613,
    0.3042356766594781,
    0.2991027885013156,
    0.2955124028523763,
    0.28963007397121854,
    0.2903970040215386,
    0.28637954499986434,
    0.2872335444556342,
    0.2829894161224365,
    0.28182132720947267,
    0.2766185347239176,
    0.2772893640730116,
    0.27366411103142635,
    0.2758428213331434,
    0.2717382738325331,
    0.2714681529998779,
    0.26823503600226506,
    0.2718168046739366,
    0.2708843453725179,
    0.2772286563449436,
    0.27312407917446563,
    0.27701925913492836,
    0.27461402893066406,
    0.2828756607903375,
    0.2845575661129422,
    0.30074053022596575,
    0.3037731774648031,
    0.32245770348442926,
    0.3257169246673584,
    0.3456558322906494,
    0.34817435794406476,
    0.3611153390672472,
    0.36257067362467454,
    0.3739259931776258,
    0.3748758655124241,
    0.38304985894097215,
    0.38108903461032445,
    0.385062616136339,
    0.3793545956081814,
    0.3809059672885471,
    0.3753546439276801,
    0.37817868762546114,
    0.3742570241292318,
    0.3773597653706869,
    0.3730721452501085,
    0.37449275546603733,
    0.36941215727064347,
    0.37046673668755425,
    0.36612689759996203,
    0.36627506468031146,
    0.35996568891737196,
    0.357708617316352,
    0.3508240254720052,
    0.34973464330037435,
    0.34625750011867945,
    0.3459699291653104,
    0.33904182646009656,
    0.33365614997016063,
    0.3253074582417806,
    0.3201222356160482,
    0.3155642933315701,
    0.3125750944349501,
    0.3110150888231065,
    0.31168614281548396,
    0.31150312847561307,
    0.313089173634847,
    0.31282772064208986,
    0.31268829345703125,
    0.31056188371446397,
    0.3103876876831055,
    0.30875801510281037,
    0.30793023427327476,
    0.30846181657579214,
    0.3090980381435818,
    0.3096993086073134,
    0.31105865266588,
    0.31017843882242835,
    0.3106839095221625,
    0.30881891250610355,
    0.30998666551378035,
    0.3084790378146702,
    0.30738966200086804,
    0.3049495760599772,
    0.30183853149414064,
    0.2979692628648546,
    0.2944834603203667,
    0.2919039429558648,
    0.2886969926622179,
    0.2865532133314344,
    0.2844181866115994,
    0.28240513695610897,
    0.2808626619974772,
    0.27920688417222767,
    0.2787711673312717,
    0.2787275907728407,
    0.27885830561319985,
    0.2790848837958442,
    0.277010809580485,
    0.27609573152330186,
    0.2759997982449001,
    0.2767840915256076,
    0.2796512307061089,
    0.2812808566623264,
    0.28181243896484376,
    0.28278850131564676,
    0.2808799574110243,
    0.28165555318196617,
    0.2803483581542969,
    0.2807318030463325,
    0.28052263471815325,
    0.27938976287841794,
    0.2791370434231228,
    0.2794594785902235,
    0.28040935940212675,
    0.27957277086046006,
    0.27592137230767144,
    0.27586908976236985,
    0.2717296557956272,
    0.27151179843478734,
    0.2691240056355794,
    0.26888000064426,
    0.2665009307861328,
    0.2689148712158203,
    0.2688626437717014,
    0.26946395026312936,
    0.26784302181667746,
    0.2672417153252496,
    0.2655772484673394,
    0.26767746395534936,
    0.26973410288492833,
    0.2736992475721571,
    0.27598252614339197,
    0.2789890586005317,
    0.27899781545003255,
    0.28042701297336153,
    0.27775166829427084,
    0.2820828247070312,
    0.28372987959120005,
    0.288845329284668,
    0.2918867195977105,
    0.29410892486572265,
    0.2954335488213433,
    0.29741173214382594,
    0.29984308030870227,
    0.3022134314643012,
    0.3039650599161784,
    0.30549881829155817,
    0.30626568688286676,
    0.30678855895996093,
    0.3053681055704753,
    0.3056643803914388,
    0.3043223614162869,
    0.30298901875813805,
    0.30060125562879775,
    0.29665357377794055,
    0.293943362765842,
    0.2923573260837131,
    0.2919041951497396,
    0.2907625749376085,
    0.29044015248616534,
    0.2875295045640734,
    0.28746852027045355,
    0.284043706258138,
    0.2812898847791883,
    0.27844896104600697,
    0.27383898841010196,
    0.271825926038954,
    0.2701440217759874,
    0.26933356391059027,
    0.2670416344536675,
    0.26551659478081596,
    0.26359066009521487,
    0.26373009575737844,
    0.2645928446451823,
    0.26659719255235464,
    0.26752965715196403,
    0.26813096788194446,
    0.2686625205145942,
    0.26915927886962887,
    0.26796536763509116,
    0.2681135347154405,
    0.26586516910129127,
    0.2659610133700901,
    0.2663357586330838,
    0.2666494878133138,
    0.26900241427951394,
    0.2667976294623481,
    0.2649326833089192,
    0.2615601433648003,
    0.2575601577758789,
    0.2553989664713542,
    0.25144253624810115,
    0.2488891643948025,
    0.24686730278862848,
    0.243451173570421,
    0.24289336734347874,
    0.2391983328925239,
    0.23500657823350693,
    0.22967318216959634,
    0.2260217963324653,
    0.22466230604383683,
    0.223912845187717,
    0.2245577324761285,
    0.2236775588989258,
    0.2222745132446289,
    0.21899784935845268,
    0.21945972866482202,
    0.21755993949042426,
    0.21691505432128907,
    0.21555558522542317,
    0.21414381451076933,
    0.21477996614244246,
    0.21519826889038085,
    0.21858826107449003,
    0.21914596981472437,
    0.22061876085069443,
    0.22162093692355686,
    0.22196949005126954,
    0.22258822123209634,
    0.2219782002766927,
    0.22240520477294923,
    0.22251850552029082,
    0.22350325690375436,
    0.22626576317681205,
    0.2285141075981988,
    0.23296725379096136,
    0.23262740241156687,
    0.235294066535102,
    0.23110233306884767,
    0.23092804378933374,
    0.2286535178290473,
    0.2296382988823785,
    0.23260996924506294,
    0.23542476230197484,
    0.23567747751871745,
    0.23469278547498917,
    0.23218296898735893,
    0.23369059244791668,
    0.23574725257025822,
    0.24094994015163848,
    0.24100221845838757,
    0.24264060126410592,
    0.24001750098334418,
    0.23665367126464842,
    0.2357996368408203,
    0.23289768642849393,
    0.2307016118367513,
    0.23002191331651475,
    0.22816571129692922,
    0.22847073449028865,
    0.22723325941297742,
    0.22653611077202693,
    0.2246363491482205,
    0.22361673143174912,
    0.2229108640882704,
    0.22199580722384982,
    0.22057533688015407,
    0.21837925804985894,
    0.2186319563123915,
    0.21886726803249787,
    0.21913743336995442,
    0.21941634707980684,
    0.21763854556613496,
    0.21521588643391928,
    0.21397840711805557,
    0.21189562903510198,
    0.21163419935438368,
    0.21125074598524304,
    0.2112071948581272,
    0.21224424574110246,
    0.21231394873725043,
    0.21331613752577042,
    0.2129762691921658,
    0.21232267167833116,
    0.21051873948838976,
    0.2081135008070204,
    0.2052637905544705,
    0.20346856011284722,
    0.20270166609022353,
    0.20213523864746094,
    0.2031897015041775,
    0.20250127156575518,
    0.20212653266059025,
    0.2008977762858073,
    0.1995731692843967,
    0.19631386227077907,
    0.19200880686442057,
    0.18755552927652996,
    0.18296289232042098,
    0.17933760748969185,
    0.1733854971991645,
    0.1679998779296875,
    0.16341601053873697,
    0.1596077389187283,
    0.1587101279364692,
    0.15628748151991104,
    0.15312408023410373,
    0.1511197280883789,
    0.14834849463568794,
    0.1461262681749132,
    0.14393018934461804,
    0.1416992653740777,
    0.1395467546251085,
    0.13762955983479816,
    0.13574721866183811,
    0.13328971862792968,
    0.13049235026041664,
    0.12921131134033204,
    0.12691939883761935,
    0.1248540539211697,
    0.12095866309271919,
    0.11617435031467012,
    0.11283668729994033,
    0.10989985783894857,
    0.10962098651462131,
    0.11027459886338975,
    0.11028331544664172,
    0.1090807024637858,
    0.10587373521592881,
    0.10213515811496311,
    0.09880615658230252,
    0.09730724546644422,
    0.09623534520467121,
    0.09762097888522679,
    0.09670593473646376,
    0.09560787836710612,
    0.0928453403049045,
    0.09173860549926759,
    0.08954250971476237,
    0.0883224572075738,
    0.08795645183987089,
    0.0867886839972602,
    0.08787800470987955,
    0.0862222311231825,
    0.08484532250298395,
    0.08261437733968098,
    0.07950325859917534,
    0.07721132490370008,
    0.07629628923204211,
    0.07505880567762586,
    0.07279301537407769,
    0.06941176096598307,
    0.06462745454576281,
    0.06332027223375108,
    0.06049674246046278,
    0.058980403476291236,
    0.05719391610887315,
    0.05385623931884765,
    0.05240090158250597,
    0.05193030251397027,
    0.051930299335055885,
    0.05132899814181857,
    0.048191744486490884,
    0.04540307998657226,
    0.04264055040147569,
    0.03984316190083822,
    0.03850982666015625,
    0.03417867130703397,
    0.032514181137084965,
    0.03186058150397406,
    0.02992594083150228,
    0.02957735856374105,
    0.028592608239915634,
    0.03044010268317329,
    0.030945555369059245,
    0.030745111571417915,
    0.028549031681484646,
    0.025690653059217663,
    0.025629647572835285,
    0.02738128079308404,
    0.027973878648546006,
    0.027834439277648924,
    0.026248382992214627,
    0.02387801700168186,
    0.021716793908013236,
    0.01938999573389689,
    0.017917226950327558,
    0.018161233133739896,
    0.01798694199985928,
    0.0203050246503618,
    0.01953814148902893,
    0.01871025330490536,
    0.016801757083998784,
    0.013830076356728872,
    0.013795218235916562,
]


def remove_outliers(x_values, y_values, threshold=2):

    z_scores = zscore(y_values)  # Calculate Z-scores for y values
    filter_mask = (
        np.abs(z_scores) < threshold
    )  # Create a boolean mask where Z-scores < threshold

    # Filter out x and y values based on Z-score threshold
    cleaned_x = np.array(x_values)[filter_mask]
    cleaned_y = np.array(y_values)[filter_mask]

    return cleaned_x, cleaned_y


def plot_spectrum_with_regression(
    x_values, y_values, title, xlabel, ylabel, saveFilename, remove_outliers_flag=False
):

    # Optionally remove outliers
    if remove_outliers_flag:
        x_values, y_values = remove_outliers(x_values, y_values)

    # Create Scatter Plot
    plt.scatter(x_values, y_values, color="blue", label="Data Points")

    # Reshape X Values For Linear Regression
    x_values_reshaped = np.array(x_values).reshape(-1, 1)

    # Perform Linear Regression
    reg = LinearRegression().fit(x_values_reshaped, y_values)

    # Predict The Y Values Using The Best Fit Line
    y_pred = reg.predict(x_values_reshaped)

    # Plot Best Fit Line
    plt.plot(x_values, y_pred, color="red", label="Best Fit Line")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.legend()
    plt.xlim(min(x_values), max(x_values))
    plt.ylim(min(y_values) - 0.1, max(y_values) + 0.1)

    plt.savefig(saveFilename)
    plt.show()


def absorbance_with_regression(remove_outliers_flag=False):
    global saveFilename

    # Capture The Reference Spectrum
    spectrum = capture()

    # Calculate The Absorbance Spectrum And Normalize It
    absorbances = normalise(absorbance(reference, spectrum))

    # Get Wavelength Axis With Regression
    params = np.polyfit(pixel, wavelength, 3)
    nmAxis = np.polyval(params, range(len(spectrum)))

    # Plot Absorbance Spectrum With Regression and Optional Outlier Removal
    plot_spectrum_with_regression(
        nmAxis,
        absorbances,
        "Absorbance Spectrum",
        "Wavelength (nm)",
        "Absorbance",
        saveFilename,
        remove_outliers_flag,
    )


def transmitance_with_regression(remove_outliers_flag=False):
    global saveFilename

    # Capture The Reference Spectrum
    spectrum = capture()

    # Calculate The Transmitance Spectrum And Normalize It
    transmitances = normalise(transmittance(reference, spectrum))

    # Get Wavelength Axis With Regression
    params = np.polyfit(pixel, wavelength, 3)
    nmAxis = np.polyval(params, range(len(spectrum)))

    # Plot Transmitance Spectrum With Regression and Optional Outlier Removal
    plot_spectrum_with_regression(
        nmAxis,
        transmitances,
        "Transmitance Spectrum",
        "Wavelength (nm)",
        "Transmitance",
        saveFilename,
        remove_outliers_flag,
    )


def reflectance_with_regression(remove_outliers_flag=False):
    global saveFilename

    # Capture The Reference Spectrum
    spectrum = capture()

    # Calculate The Reflectance Spectrum And Normalize It
    reflectances = normalise(reflectance(reference, spectrum))

    # Get Wavelength Axis With Regression
    params = np.polyfit(pixel, wavelength, 3)
    nmAxis = np.polyval(params, range(len(spectrum)))

    # Plot Reflectance Spectrum With Regression and Optional Outlier Removal
    plot_spectrum_with_regression(
        nmAxis,
        reflectances,
        "Reflectance Spectrum",
        "Wavelength (nm)",
        "Reflectance",
        saveFilename,
        remove_outliers_flag,
    )


# ================================================================================================= #


import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import threading
import time  # For simulating long-running tasks


class SpectrumAnalysisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Spectrum Analysis")
        self.geometry("500x500")
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        self.title_label = ctk.CTkLabel(
            self, text="Spectrum Analysis", font=("Consolas", 24, "bold")
        )
        self.title_label.place(x=150, y=20)

        # File Name Entry
        self.file_name_entry = ctk.CTkEntry(
            self, placeholder_text="Enter Plot Name", width=250
        )
        self.file_name_entry.place(x=50, y=100)

        self.save_button = ctk.CTkButton(
            self, text="Initialize", command=self.save_plot
        )
        self.save_button.place(x=320, y=100)

        # Spectrum Type Menu
        self.spectrum_type_var = tk.StringVar(value="Select Spectrum Type")
        self.spectrum_type_menu = ctk.CTkOptionMenu(
            self,
            values=["Reflectance", "Absorbance", "Transmitance"],
            command=self.spectrum_type_callback,
            variable=self.spectrum_type_var,
            state="disabled",
        )
        self.spectrum_type_menu.place(x=50, y=150)

        # Remove Outliers Checkbox
        self.remove_outliers_var = tk.StringVar(value="True")
        self.remove_outliers_checkbox = ctk.CTkSwitch(
            self,
            text="Remove Outliers",
            variable=self.remove_outliers_var,
            onvalue="True",
            offvalue="False",
            state="disabled",
        )
        self.remove_outliers_checkbox.place(x=320, y=150)

        # Capture & Analyze Button
        self.capture_button = ctk.CTkButton(
            self,
            text="Capture & Analyze",
            command=self.capture_and_analyze,
            state="disabled",
        )
        self.capture_button.place(x=50, y=200)

        # Log Frame
        self.log_frame = ctk.CTkFrame(self, width=405, height=100)
        self.log_frame.place(x=50, y=250)

        # Status Label
        self.status_label = ctk.CTkLabel(self.log_frame, text="")
        self.status_label.place(x=10, y=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.log_frame, orientation="horizontal", mode="indeterminate", width=405
        )
        self.progress_bar.place(x=0, y=90)

        # Theme Selection Dropdown
        self.theme_var = tk.StringVar(value="Dark")
        self.theme_menu = ctk.CTkOptionMenu(
            self,
            values=["Dark", "Light"],
            command=self.change_theme,
            variable=self.theme_var,
        )
        self.theme_menu.place(x=50, y=400)

    def spectrum_type_callback(self, choice):
        print(f"[ - ] Spectrum Type : {choice}")

    def capture_and_analyze(self):
        spectrum_type = self.spectrum_type_var.get()
        remove_outliers = self.remove_outliers_var.get()

        if not self.file_name_entry.get():
            self.status_label.configure(
                text="Please Enter a Plot Name Before Capturing and Analyzing"
            )
            return

        global saveFilename
        saveFilename = self.file_name_entry.get() + ".png"

        spectrum_type = self.spectrum_type_var.get()
        remove_outliers_flag = self.remove_outliers_var.get() == "True"

        self.status_label.configure(text="Capturing And Analyzing...")
        self.progress_bar.start()  # Start the progress bar

        # Simulate a long-running task with threading
        self.thread = threading.Thread(
            target=self.analyze_spectrum, args=(spectrum_type, remove_outliers_flag)
        )
        self.thread.start()

    def analyze_spectrum(self, spectrum_type, remove_outliers_flag):
        

        if spectrum_type == "Reflectance":
            print("[ - ] Analyzing Reflectance Spectrum")
            reflectance_with_regression(remove_outliers_flag)

        elif spectrum_type == "Absorbance":
            print("[ - ] Analyzing Absorbance Spectrum")
            absorbance_with_regression(remove_outliers_flag)

        elif spectrum_type == "Transmitance":
            print("[ - ] Analyzing Transmitance Spectrum")
            transmitance_with_regression(remove_outliers_flag)

        time.sleep(3)  # Simulate long-running task

        # Analysis complete
        self.after(0, self.on_analysis_complete)

    def on_analysis_complete(self):
        self.progress_bar.stop()  # Stop the progress bar
        self.status_label.configure(text="Analysis Complete !")

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)
        self.theme_var.set(choice)
        print(f"[ - ] Theme changed To : {choice}")

    def save_plot(self):
        file_name = self.file_name_entry.get()

        self.spectrum_type_menu.configure(state="normal")
        self.remove_outliers_checkbox.configure(state="normal")
        self.capture_button.configure(state="normal")

        if not file_name:
            self.status_label.configure(text="Please Enter A Plot Name")
            return

        global saveFilename
        saveFilename = file_name + ".png"
        self.status_label.configure(text=f"Plot Will Saved As : {saveFilename}")


if __name__ == "__main__":
    app = SpectrumAnalysisApp()
    app.mainloop()
