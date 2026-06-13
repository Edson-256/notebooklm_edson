#!/usr/bin/env python3
"""
Build do projeto Paradise Lost (Leitura Formativa COF).

Monta, a partir das 55 cenas levantadas livro-a-livro (12 analistas COF):
  - PL-capitulos/                     (os 12 Livros renomeados + _capitulos_index.json)
  - _cenas_manifest.json              (seq_global continuo; cap = Livro; cena_local por Livro)
  - _anchors.json                     (inicio/fim por seq_global)

QC CRITICO: cada ancora (inicio/fim) e verificada contra o TEXTO REAL do Livro usando a MESMA
regex tolerante a espacos/quebras (\\s+) que o 04_build_nlm_source.py usa. Se a ancora crua nao
casar, tenta versoes sem aspas (retas/curvas) ao redor. Ancoras que nao casarem sao REPORTADAS.
"""
from __future__ import annotations
import json, re, shutil, sys, unicodedata
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
CHAPTERS = PROJ / "output" / "chapters"
CAPDIR = PROJ / "PL-capitulos"

# Livro -> arquivo-fonte (front matter C001 fica de fora; Livros 1..12 = C002..C013)
BOOK_FILE = {b: f"C{b+1:03d}-Part-{b}.md" for b in range(1, 13)}

# (book, cena_local, titulo, localizacao, pilar, resumo, justificativa, anc_inicio, anc_fim)
SCENES = [
 # ---------------- Livro 1 ----------------
 (1,1,'A invocação: "justify the ways of God to men"','abertura do Livro 1 — a proposição e a invocação à Musa','meio',
  "O poeta anuncia o tema — a primeira desobediência do homem e a perda do Éden até que 'um Homem maior' nos restaure — e invoca a Musa Celeste e o Espírito para iluminar o que nele é escuro. Declara seu propósito: afirmar a Providência Eterna e justificar os caminhos de Deus aos homens.",
  "A abertura enuncia o poema como caminho de conhecimento ('this great argument'), convidando o ouvinte a ler a obra como filosofia do viver, não mero relato — e a vestir a voz que ousa pedir luz para o que é escuro em si mesmo.",
  "Of Man's first disobedience, and the fruit","And justify the ways of God to men."),
 (1,2,'Satã desperta no lago de fogo: "darkness visible"','o lago de fogo; Satã, vencido, ergue os olhos sobre o Inferno','intuicao',
  "Despertado da queda, Satã lança os olhos sombrios em redor e contempla a masmorra horrível, fornalha em chamas de onde não brota luz mas 'trevas visíveis', que só revelam regiões de dor onde paz e esperança jamais habitam. A seu lado avista Belzebu, o próximo em poder e em crime.",
  "Antes de qualquer raciocínio, a cena pede que o ouvinte SINTA o Inferno — o calor, a 'darkness visible', o desespero — habitando a percepção do anjo caído antes de julgá-lo.",
  "Torments him: round he throws his baleful eyes,","One next himself in power, and next in crime,"),
 (1,3,'"The mind is its own place"','em terra firme, ao alcançar a praia do Inferno; primeiro discurso de Satã','meio',
  "Já em terra, Satã pergunta se é esta a região que devem trocar pelo Céu, saúda o mundo infernal e proclama que traz 'uma mente que lugar ou tempo não mudam', pois a mente é seu próprio lugar e pode fazer um Céu do Inferno e um Inferno do Céu.",
  "É o coração da through-line: a mente como cápsula fechada que se basta a si mesma ('myself am Hell' em germe), oposta ao 'paraíso interior' prometido no fim. Vestir a pele de Satã para reconhecer o próprio cárcere.",
  '"Is this the region, this the soil, the clime,"',"Can make a Heaven of Hell, a Hell of Heaven."),
 (1,4,'"Better to reign in Hell than serve in Heaven"','a praia do lago de fogo; o brado que reúne as legiões','sinceridade',
  "Satã conclui que é melhor reinar no Inferno do que servir no Céu e resolve reerguer os companheiros prostrados. Caminha até a praia do mar inflamado e chama as legiões — espessas como folhas outonais — com o brado 'Awake, arise, or be for ever fallen!', e elas se erguem.",
  "A escolha nua de Satã — preferir o domínio na ruína à submissão — expõe a verdade moral crua do orgulho que não cede; o ouvinte sente por dentro a sedução real de reinar sobre o próprio inferno.",
  "To reign is worth ambition, though in Hell:",'Awake, arise, or be for ever fallen!"'),
 (1,5,'Pandæmonium ergue-se e o grande conselho é convocado','a colina vulcânica do Inferno; a construção de Pandæmonium','memoria',
  "Sob o comando de Mammon extrai-se ouro das entranhas da colina e, com arte prodigiosa, um edifício imenso ergue-se 'como uma exalação' — Pandæmonium, a alta capital de Satã. Os arautos proclamam o conselho; a multidão, reduzida a formas mínimas, aflui, e o grande consulto começa.",
  "O palácio infernal brotando do solo 'like an exhalation', com sua música e ouro, é um quadro vivíssimo a guardar e reativar diante de toda 'magnificência' construída sobre a ruína.",
  "There stood a hill not far, whose grisly top","And summons read, the great consult began."),
 # ---------------- Livro 2 ----------------
 (2,1,'O Concílio Infernal: Moloch, Belial e Mammon','o trono no Pandæmonium; o grande conselho dos anjos caídos','sinceridade',
  "Três conselheiros falam: Moloch defende a guerra aberta e desesperada; Belial, eloquente e covarde, aconselha a inação disfarçada de prudência; Mammon propõe renunciar ao Céu e erguer no Inferno um império próprio. O conselho aplaude Mammon, temendo nova batalha mais que o próprio inferno.",
  "As três vozes expõem, sem agenda moderna, a verdade nua de cada postura diante da derrota — fúria, covardia racionalizada e resignação ao conforto. O ouvinte habita vicariamente cada antagonista e reconhece essas tentações em si.",
  "He ceased; and next him Moloch, sceptred king,","In emulation opposite to Heaven."),
 (2,2,'Belzebu revela o plano contra o Homem; Satã se oferece','o concílio; a fala decisiva de Belzebu e a resolução de Satã','meio',
  "Belzebu, erguendo-se como um pilar de Estado, desvia o conselho da inércia e propõe corromper o novo mundo — a raça chamada Homem — como vingança contra Deus. Aprovado o plano, todos calam-se amedrontados diante da travessia do Abismo, até que Satã, por orgulho monárquico, assume sozinho a missão.",
  "A falsa magnanimidade de Satã, que despreza a própria segurança 'pela salvação geral', revela como o orgulho mascara o egoísmo — uma filosofia de viver pela contramão: o eu que se diviniza ao recusar dividir risco e honra.",
  "Which when Beelzebub perceived---than whom,","Thus they their doubtful consultations dark"),
 (2,3,'Os passatempos dos caídos: "in wandering mazes lost"','as regiões do Inferno enquanto Satã parte','intuicao',
  "Dissolvido o concílio, as legiões entretêm as horas: umas competem em jogos, outras cantam seus feitos, e outras, à parte numa colina, raciocinam alto sobre Providência, presciência, vontade e destino, sem encontrar fim, perdidas em labirintos. Outras exploram os quatro rios infernais, achando só um universo de morte.",
  "A 'vain wisdom' dos filósofos perdidos nos labirintos mostra, pela experiência antes do raciocínio, que a razão fechada em si mesma só gera 'fallacious hope', nunca o paraíso interior.",
  "The Stygian council thus dissolved; and forth","Gorgons, and Hydras, and Chimeras dire."),
 (2,4,'No portão do Inferno: Pecado e Morte, a alegoria da consequência','os tríplices portões do Inferno','memoria',
  "Satã depara com duas formas monstruosas: uma mulher que termina em serpente, cercada de cães infernais, e uma sombra negra coroada. Prestes a lutar, descobre que ela é o Pecado, nascido de sua própria cabeça, e o outro é a Morte, filho incestuoso deles. Reconhecida a filha, promete libertá-los, e ela abre os portões.",
  "A imagem horrenda — o Pecado parindo a Morte, devorado eternamente pela própria prole — é uma alegoria viva da consequência: o pecado gera a morte, e o eu que se enamora da própria imagem encerra-se no inferno que procria.",
  "Before the gates there sat","Cast forth redounding smoke and ruddy flame."),
 (2,5,'A travessia do Abismo: Satã, o Caos e a velha Noite','do limiar do Inferno através do Caos','memoria',
  "Abertos os portões, descortina-se o oceano ilimitável do Abismo, onde a Noite e o Caos reinam sobre a anarquia eterna dos átomos. Satã lança-se na vastidão, despenca, é arremessado por nuvens de fogo e luta meio voando, meio nadando até a corte do Caos, de quem obtém o caminho para a luz, e salta adiante como uma pirâmide de fogo.",
  "A travessia heroica e solitária pelo caos informe imprime a vivência do eu que prossegue 'só e sem guia, meio perdido', aliando-se à própria desordem para alimentar a vingança — imagem do esforço titânico desperdiçado em ruína.",
  "Before their eyes in sudden view appear","Accursed, and in a cursed hour, he hies."),
 # ---------------- Livro 3 ----------------
 (3,1,'"Hail, holy Light" — a cegueira e a luz interior','proêmio do Livro 3 — a invocação à Luz','sinceridade',
  "Milton saúda a Luz sagrada e celebra seu retorno do abismo onde cantou o Caos. Confessa que essa luz não revisita seus olhos cegos: as estações voltam, mas para ele não volta o dia nem a face humana, só a treva. Pede então que a Luz celestial brilhe por dentro e irradie a mente, para ver e dizer o invisível.",
  "A confissão nua da cegueira — sem autopiedade encenada — é verdade humana crua: o poeta converte a perda real em súplica por visão interior. O ouvinte sente, por dentro, a perda da luz e o anseio que a substitui.",
  "Hail, holy Light, offspring of Heaven firstborn,","Of things invisible to mortal sight."),
 (3,2,'"Sufficient to have stood, though free to fall"','no Céu — Deus contempla Satã e fala ao Filho','meio',
  "Do alto trono, Deus prevê que o homem cairá ao ceder à tentação, mas declara a culpa inteiramente humana: criou-o justo e reto, suficiente para ter resistido, ainda que livre para cair. Defende o livre-arbítrio: anjos e homens caíram por escolha própria, não por decreto, e a presciência não constrange a falta.",
  "A defesa do livre-arbítrio é filosofia do viver: sem liberdade não há mérito, amor nem fé sinceros. O ouvinte é levado ao autoconhecimento — sou 'autor de mim mesmo' e não posso acusar fado ou Criador pela minha queda.",
  "Now had the Almighty Father from above,","But Mercy, first and last, shall brightest shine."),
 (3,3,'"Behold me then: me for him" — o Filho se oferece','no Céu — após o silêncio do coro celeste','intuicao',
  "Deus pergunta onde se acharia tal amor capaz de morrer para redimir o homem, e o Céu inteiro emudece. Então o Filho, em quem habita a plenitude do amor divino, oferece-se: vida por vida, que sobre ele caia a ira e a morte; mas anuncia que ressurgirá vitorioso, conduzindo o Inferno cativo e seus redimidos ao Céu.",
  "O amor sacrificial não nasce de cálculo, mas de um movimento do ser que se entrega antes de qualquer razão — contra-imagem exata da autoafirmação de Satã. O ouvinte experimenta o gesto que quebra a cápsula do eu.",
  "But yet all is not done; Man disobeying,","Of his great Father. Admiration seized"),
 (3,4,'"The false dissembler unperceived" — Satã engana Uriel','no globo do novo mundo; Satã aborda o Arcanjo Uriel','memoria',
  "Satã muda de forma, fingindo-se um jovem Querubim de rosto sorridente, e aborda Uriel com falsa devoção, alegando desejo de louvar o homem. Assim fala o dissimulador, despercebido — pois a hipocrisia é o único mal que caminha invisível, exceto a Deus. Iludido, o mais agudo dos espíritos aponta-lhe o caminho do Paraíso.",
  "A imagem do hipócrita de rosto santo — 'a bondade não pensa mal onde mal não parece' — é viva e deve ser guardada para evocar sempre que o mal se disfarce de bem.",
  "But first he casts to change his proper shape,","In his uprightness, answer thus returned."),
 # ---------------- Livro 4 ----------------
 (4,1,'"Myself am Hell" — o solilóquio no Monte Niphates','a encosta do monte, diante do Éden, ao meio-dia','sinceridade',
  "Antes de atacar o homem, Satã é assaltado por consciência, dúvida e horror; reconhece que sua queda nasceu do próprio orgulho e que nenhuma fuga é possível, pois carrega o inferno dentro de si. Recusa o arrependimento por medo da vergonha e abjura todo bem com 'Evil, be thou my good'.",
  "É o cume da verdade humana crua e do dilema moral: o ser fechado que se autocondena ao declarar 'myself am Hell', recusando a submissão que o libertaria. Vivência vicária máxima da cápsula individual lacrada.",
  "Me miserable! which way shall I fly",'As Man ere long, and this new world, shall know."'),
 (4,2,'"In naked majesty" — a primeira visão de Adão e Eva','o interior do Paraíso, onde Satã observa o casal','intuicao',
  "Satã, e com ele o leitor, contempla pela primeira vez Adão e Eva eretos em majestade nua, imagem viva do Criador, andando de mãos dadas sem culpa nem vergonha. A descrição une beleza, inocência prelapsariana e o amor do par mais belo já reunido em abraços.",
  "A cena pede que se sinta a inocência antes de qualquer raciocínio sobre a Queda — o leitor habita o olhar maravilhado (e invejoso) de Satã diante do bem, abrindo uma fresta na cápsula do eu fechado.",
  "Two of far nobler shape, erect and tall,","That ever since in love's embraces met;"),
 (4,3,'"Another sky" — Eva diante de sua imagem no lago','a margem de um lago, no relato de Eva a Adão','memoria',
  "Eva recorda o dia em que despertou para a vida e, atraída por um som de águas, debruçou-se sobre um lago onde uma forma respondia a seus olhares com amor — sua própria imagem. Uma voz a adverte de que aquilo é ela mesma e a conduz a Adão, de quem ela é 'carne e osso'.",
  "É o narciso prelapsariano: o eu prestes a fixar-se na própria imagem e resgatado para o outro. Imagem viva a guardar — a saída da cápsula individual rumo ao paraíso partilhado.",
  "That day I oft remember, when from sleep","How beauty is excelled by manly grace,"),
 (4,4,'"Hail, wedded Love" — a oração da noite e o caramanchão','o caramanchão nupcial, ao crepúsculo','meio',
  "Sob a Noite e a lua, Adão e Eva conversam sobre o repouso e as estrelas, adoram juntos o Criador a céu aberto e entram no caramanchão, onde o poeta celebra o amor conjugal puro como fonte de toda relação humana. Adormecem abraçados, exortados a não buscar estado mais feliz.",
  "O ideal do casamento prelapsariano é passo de autoconhecimento e filosofia do bem viver: o eu se completa no 'mútuo auxílio e mútuo amor' — o paraíso interior como comunhão, antípoda da cápsula de Satã.",
  "When Adam thus to Eve. Fair Consort, the hour","And on their naked limbs the flowery roof"),
 (4,5,'"Squat like a toad" — Satã descoberto e pesado nas balanças','o caramanchão de Eva, sob a guarda de Gabriel','memoria',
  "Ithuriel e Zéfon encontram Satã agachado como um sapo ao ouvido de Eva, forjando sonhos; o toque da lança o restitui à própria forma e o leva ao confronto com Gabriel. Quando a ameaça de combate cresce, Deus suspende no céu suas balanças de ouro, e Satã, pesado e achado leve, foge nas sombras.",
  "Imagem inesquecível: o sapo no ouvido, a verdade que não suporta o toque celeste, as balanças que medem o eu rebelde e o acham 'leve e fraco'. O eu fechado é exposto, pesado e desfeito pela ordem divina.",
  "Squat like a toad, close at the ear of Eve,","Murmuring, and with him fled the shades of night."),
 # ---------------- Livro 5 ----------------
 (5,1,'O sonho de Eva: "of offence and trouble"','o leito nupcial, ao alvorecer','sinceridade',
  "Eva conta o sonho inquietante em que uma voz a leva à árvore proibida, onde uma figura prova o fruto e a tenta a ascender entre os deuses. Adão, entristecido, consola-a explicando que a Fantasia, na ausência da Razão, forja imagens errantes nos sonhos — e que abominar o mal sonhando é sinal de que jamais consentirá nele.",
  "O sonho expõe, em estado bruto, a primeira fissura moral na alma de Eva, e a resposta de Adão revela a verdade de uma consciência que teme ter ofendido. Romper a cápsula começa por encarar com sinceridade o que se agita no fundo de si.",
  "But of offence and trouble, which my mind","So all was cleared, and to the field they haste."),
 (5,2,'Rafael, o hóspede: "freely we serve, because we freely love"','o caramanchão, ao meio-dia; a visita do anjo','meio',
  "Rafael desce ao Paraíso como amigo e hóspede, partilha a refeição e ensina a Adão a escala da natureza. Adverte que Deus o fez perfeito mas mutável: a felicidade depende da obediência livremente escolhida, pois só o serviço voluntário — não o necessitado — se prova no amor.",
  "Rafael oferece uma filosofia do viver: a liberdade não se opõe à obediência, mas a fundamenta, porque 'servimos livremente, porque livremente amamos'. É um passo de autoconhecimento sobre a natureza do próprio querer.",
  "Adam, I therefore came; nor art thou such","And so from Heaven to deepest Hell; O fall"),
 (5,3,'A revolta no Norte: o orgulho ferido de Satã','no Céu, em retrospecto narrado por Rafael','memoria',
  "Rafael narra como o Pai proclamou o Filho ungido, exigindo que toda joelho se dobrasse — e como Satã, ferido de orgulho e inveja, julgou-se diminuído. À noite, com palavras de 'verdade falsificada', desperta seu subordinado e atrai a terça parte da hoste celeste para o norte, fingindo preparar a recepção do Rei.",
  "A imagem do orgulho que se diz 'self-begot, self-raised' — recusando reconhecer o próprio Criador — é a memória-mestra de toda queda: o eu fechado que se faz origem de si mesmo, a cápsula em sua forma absoluta.",
  "Hear, all ye Angels, progeny of light,","Drew after him the third part of Heaven's host."),
 (5,4,'Abdiel, fiel entre os infiéis: "faithful only he"','o Monte da Congregação, no norte do Céu','intuicao',
  "Diante do discurso sedicioso de Satã, o serafim Abdiel levanta-se sozinho, em chama de zelo, e refuta a blasfêmia, lembrando que foi o Filho quem criou os próprios anjos. Nenhum o secunda; cercado de inimigos e coberto de escárnio, permanece 'imóvel, inabalável, não seduzido, sem temor' e parte sem se voltar.",
  "Abdiel encarna a coragem intuitiva de sentir a verdade e permanecer fiel quando 'nem número nem exemplo' o acompanham. É a vivência vicária mais poderosa do livro: dissentir da multidão sem trair o próprio eu mais verdadeiro.",
  "Abdiel, than whom none with more zeal adored","On those proud towers to swift destruction doomed."),
 # ---------------- Livro 6 ----------------
 (6,1,'Abdiel desfere o primeiro golpe da guerra','a orla da batalha, entre as duas hostes','sinceridade',
  "Abdiel, o único que dissentira sozinho, não suporta ver Satã avançar com aparência ainda semelhante à do Altíssimo e sai das fileiras para enfrentá-lo. Após refutar de novo a falsa noção de liberdade do inimigo, desfere um golpe que faz Satã recuar dez passos e cair sobre um joelho, abrindo a guerra do Céu.",
  "Abdiel encarna a verdade crua de quem ousa estar certo sozinho contra milhares; sua coragem de servir o digno, e não a si mesmo, expõe o eu fechado de Satã, 'escravo de si próprio'.",
  "Abdiel that sight endured not, where he stood","Presage of victory, and fierce desire"),
 (6,2,'A primeira dor de Satã: "then Satan first knew pain"','o coração da batalha celeste','intuicao',
  "Após longa batalha em escala equilibrada, Michael e Satã enfrentam-se corpo a corpo; a espada forjada na armaria de Deus corta o escudo e fere o lado direito do rebelde. Satã conhece a dor pela primeira vez, contorce-se, sangra, e é carregado pelos seus, humilhado ao descobrir-se não invencível.",
  "A dor irrompe como experiência sentida antes de qualquer raciocínio: o anjo que se cria igual a Deus descobre, na carne ferida, o limite de si mesmo. A rachadura na cápsula do orgulho é vivida sensorialmente, não argumentada.",
  "The battle hung; till Satan, who that day","His confidence to equal God in power."),
 (6,3,'A invenção do canhão: a pólvora arrancada do Céu','o conselho noturno dos rebeldes; o solo revolvido','memoria',
  "No conselho noturno, Satã revela ter inventado uma arma nova: das matérias escuras sob o solo celeste extraem enxofre e nitro para forjar canhões que, com fogo e estrondo, lançarão destruição. Em uma noite os rebeldes cavam, misturam e montam em segredo a artilharia.",
  "Milton fixa uma imagem viva e profética para evocar: o engenho que mais tarde 'flagelará os filhos dos homens'. A técnica desligada da verdade, buscando glória, é ícone da inteligência fechada em si, voltada para a ruína.",
  "Not uninvented that, which thou aright","With silent circumspection, unespied."),
 (6,4,'O terceiro dia: o Filho sozinho expulsa os rebeldes','o carro da Deidade Paterna avança até a borda do Céu','meio',
  "No terceiro dia, o Filho sobe sozinho ao carro flamejante do Pai e ordena que os Santos apenas observem, pois a vingança é sua. Dirige sobre os rebeldes prostrados, retém metade de sua força para não destruir mas expulsar, e os impele pela borda do Céu, de onde caem nove dias até o abismo.",
  "A vitória do Filho que age sozinho, e a contemplação silenciosa dos Santos, modelam uma filosofia do viver: o verdadeiro poder serve e é dado, não tomado por força. Reconhecer 'quem é digno de reinar' acima do eu é autoconhecimento.",
  "The chariot of Paternal Deity,","Nine days they fell: Confounded Chaos roared,"),
 # ---------------- Livro 7 ----------------
 (7,1,'"Descend from Heav\'n, Urania" — o poeta em dias maus','abertura do Livro 7 — a invocação a Urânia','sinceridade',
  "Milton invoca Urânia, não a musa pagã, mas a Sabedoria celeste, pedindo ser guiado de volta em segurança ao seu elemento terreno. Confessa cantar com voz mortal, caído em dias maus, cercado de trevas, perigos e solidão — 'yet not alone' enquanto a Musa visita seus sonos.",
  "O poeta cego e perseguido expõe sua verdade humana mais crua — o isolamento e o medo de cair como Belerofonte. A confissão de vulnerabilidade diante do ouvinte rompe a cápsula do eu.",
  "Descend from Heav'n Urania, by that name","And solitude; yet not alone, while thou"),
 (7,2,'"Silence, ye troubled waves" — o Verbo cria do Caos','o Filho parte ao abismo com o compasso de ouro','memoria',
  "O Filho onipotente cavalga sobre os Querubins até o Caos, vendo o abismo 'ultrajoso como um mar, escuro, devastado, selvagem'. Com a palavra 'Silence, ye troubled waves' ordena o fim da discórdia e, com o compasso de ouro, circunscreve o Universo, ordenando o mundo a partir da desordem.",
  "A imagem do Verbo aquietando as águas e abrindo o compasso sobre o abismo é cena viva e arquetípica para reevocar — o gesto fundador da ordem contra o caos.",
  "On heav'nly ground they stood, and from the shore","This be thy just Circumference, O World."),
 (7,3,'A Terra abre o ventre fértil — o bestiário da Criação','o sexto dia: a Terra dá à luz os animais','intuicao',
  "Ao mandado de Deus, a Terra abre seu ventre fértil e gera de uma só vez criaturas inumeráveis: o leão fulvo arranca-se do solo, o cervo ergue a cabeça ramificada, o Beemote emerge, e enxameiam a formiga providente, a abelha e as serpentes. A natureza nasce viçosa e plena em multidão.",
  "O leitor experimenta o assombro da vida brotando antes de qualquer raciocínio — sente a Terra parir o bestiário. A vivência vicária de maravilha abre a cápsula do eu para o êxtase da criação.",
  "Let th' Earth bring forth Soul living in her kinde,","Not noxious, but obedient at thy call."),
 (7,4,'"Let us make Man in our image" — a obra-mestra e o Sábado','o fim do sexto dia e o repouso do sétimo','meio',
  "Deus declara o Homem a 'obra-mestra', criado à sua imagem, dotado de 'santidade de razão' e domínio sobre a criação, mas advertido contra a Árvore proibida. Concluída a obra, o Criador retorna ao Céu entre harpas e, no sétimo dia, abençoa e santifica o Sábado, guardado não em silêncio mas em hinos.",
  "O Homem é feito 'self-knowing' e 'ereto, de fronte serena', chamado a corresponder com o Céu. Conhecer-se como imagem de Deus e perseverar reto é a própria filosofia de viver proposta ao ouvinte.",
  "With Sanctitie of Reason, might erect","With Halleluiahs: Thus was Sabbath kept."),
 # ---------------- Livro 8 ----------------
 (8,1,'"Be lowly wise" — os astros e a sabedoria da vida diária','Adão e Rafael conversam; Eva retira-se ao jardim','meio',
  "Adão pergunta sobre as desproporções do cosmos — por que corpos tão grandes giram para servir esta minúscula Terra. Rafael responde com cautela, expõe hipóteses, mas conclui que o segredo dos céus Deus reservou para si: o homem deve ser 'sabiamente humilde', viver bem este mundo e não sonhar com outros.",
  "O conselho 'be lowly wise' — 'conhecer o que está diante de nós na vida diária é a sabedoria primeira' — rompe a cápsula da curiosidade vã que encerra o eu em abstrações e o reorienta à vida concreta.",
  "When I behold this goodly Frame, this World","Not of Earth onely but of highest Heav'n."),
 (8,2,'"As new wak\'t from soundest sleep" — Adão desperta para a existência','Adão narra a Rafael sua própria origem','intuicao',
  "Adão relata seu primeiro instante de consciência: desperta na relva, ergue-se, contempla a si mesmo e ao mundo e tenta falar. Sem saber quem é nem de onde veio, dirige-se ao Sol e às criaturas perguntando como veio a ser — e intui que foi feito por algum grande Criador a quem deseja conhecer e adorar.",
  "É a experiência pura anterior ao raciocínio: Adão sente que existe e que é 'mais feliz do que sei' antes de qualquer conhecimento, e intui o Criador pela própria contingência. Vivência vicária do despertar à consciência.",
  "As new wak't from soundest sleep","And feel that I am happier then I know."),
 (8,3,'"In solitude what happiness?" — a criação de Eva','Adão dialoga com a Visão Divina; a formação de Eva','sinceridade',
  "Adão pede a Deus um companheiro, argumentando que entre desiguais não há verdadeira sociedade nem deleite mútuo; Deus o prova, contrapondo a própria solidão, e aprova o discernimento de Adão. Em transe, Adão vê Deus abrir-lhe o lado e formar uma criatura que lhe infunde no coração uma doçura nunca antes sentida.",
  "O cerne é a verdade crua da insuficiência: o eu reconhece honestamente que não se basta, que precisa de 'amor colateral'. Esse dilema da solidão é precisamente a ruptura da cápsula individual.",
  "In solitude","The spirit of love and amorous delight."),
 (8,4,'"In loving thou dost well, in passion not" — o aviso de Rafael','Adão confessa o arrebatamento; o anjo o adverte e parte','meio',
  "Adão confessa que, diante da beleza de Eva, sente uma 'comoção estranha' que o torna fraco, como se a sabedoria caísse degradada na presença dela. Rafael, de cenho contraído, adverte-o a pesar amor contra mera paixão, a não atribuir demais a uma aparência, e a deixar que o amor o eleve ao amor celeste; depois se despede.",
  "A advertência 'pesa-te a ti mesmo com ela' e 'o amor refina os pensamentos... é a escada pela qual ao amor celeste podes subir' é pedagogia do viver: ordenar a paixão pela razão, passo concreto contra o eu submetido ao impulso.",
  "here passion first I felt,","From the thick shade, and Adam to his Bowre."),
 # ---------------- Livro 9 ----------------
 (9,1,'O proêmio trágico: "I now must change those notes to tragic"','a invocação à Musa, antes do retorno de Satã','meio',
  "O poeta anuncia que não há mais conversas familiares entre Deus, o Anjo e o Homem: deve agora mudar as notas para o trágico, narrando a desconfiança imunda, a deslealdade e a desobediência. Declara esse argumento mais heroico que a ira de Aquiles ou de Turno, e pede à sua Patrona Celeste o estilo correspondente.",
  "A virada para o trágico é um passo de autoconhecimento sobre a condição humana caída — uma filosofia do viver que reconhece que a queda nasce do interior, não da força exterior.",
  "Those Notes to Tragic; foul distrust, and breach","Not Hers who brings it nightly to my Ear."),
 (9,2,'O debate da separação: "let us divide our labours"','o jardim, ao amanhecer, antes do trabalho','sinceridade',
  "Eva propõe dividir o trabalho, argumentando que juntos demoram e que sua firmeza não deveria ser posta em dúvida só porque existe um inimigo. Adão reluta, lembrando o Inimigo que espreita e o perigo de se separarem, mas por fim cede à autonomia dela: 'vai em tua nativa inocência'.",
  "Aqui está o dilema moral cru de uma pequena decisão fatal: o desejo de Eva de provar sua virtude sozinha contra o amor protetor de Adão. A autonomia que se fecha em si mesma — a cápsula querendo afirmar-se — é o nó da cena.",
  "Let us divide our labours, thou where choice","So bent, the more shall shame him his repulse."),
 (9,3,'A aproximação lisonjeira da Serpente: a besta que fala','entre as roseiras, onde Eva trabalha sozinha','memoria',
  "A Serpente, bela e ereta sobre seus anéis, aproxima-se de Eva com gestos de adoração e começa sua tentação chamando-a de único Prodígio, Deusa entre Deuses, vista apenas por um homem. Eva, maravilhada, pergunta como uma besta muda recebeu voz e sentido humanos.",
  "A imagem viva da serpente lustrosa, de crista erguida e olho de carbúnculo, ondulando em laços enquanto fala, é um quadro sensorial a guardar. O espanto vicário do prodígio marca a alma antes do raciocínio.",
  "His fraudulent temptation thus began.","Say, for such wonder claims attention due."),
 (9,4,'O discurso da tentação: "ye shall be as Gods"','junto à Árvore proibida, aonde a Serpente a conduziu','meio',
  "Conduzida à Árvore do conhecimento, Eva ouve a Serpente, erguida como um orador, negar a ameaça de morte e argumentar que o fruto dá vida ao conhecimento. A retórica culmina na promessa de que, comendo, seus olhos se abrirão e 'sereis como deuses', instigando-a a colher e provar livremente.",
  "A sofística da Serpente é a falsa filosofia de viver que seduz a razão fechada em si: o eu que se quer divinizar sem Deus. Compreender vicariamente como a mentira se veste de razão é passo decisivo de autoconhecimento.",
  "O Sacred, Wise, and Wisdom-giving Plant,","Goddess humane, reach then, and freely taste."),
 (9,5,'Eva come e delibera: partilhar "in bliss or woe"','junto à Árvore; o monólogo interior de Eva','sinceridade',
  "Eva colhe e come; a Terra sente a ferida e a Natureza geme. Saciada e exaltada como por vinho, ela delibera se deve esconder o conhecimento de Adão para tornar-se superior, mas, temendo a morte e que Adão viva com outra Eva, resolve partilhar com ele em bem ou em mal, por amor.",
  "A deliberação interior de Eva expõe a verdade humana mais crua: o cálculo entre poder, ciúme e amor dentro da cápsula do eu. A escolha de partilhar nasce tanto do amor quanto do medo do abandono — dilema moral nu.",
  "So saying, her rash hand in evil hour","So dear I love him, that with him all deaths"),
 (9,6,'A escolha de Adão: "with thee certain my resolution is to die"','junto à Árvore e depois no leito de flores','intuicao',
  "Adão, sabendo do que Eva fez, fica atônito e a guirlanda lhe cai da mão; mas resolve cair com ela por amor, declarando que sua resolução é morrer com ela. Come contra o seu melhor juízo, a Terra estremece, e seguem-se o desejo carnal, a vergonha após o sono e a acusação mútua sem fim.",
  "A escolha de Adão é vivida antes de raciocinada — 'o elo da natureza me atrai' — intuição do amor que, ao romper a cápsula do eu para unir-se a Eva, paradoxalmente os fecha juntos na queda. Sente-se o peso antes de julgá-lo.",
  "O fairest of Creation, last and best","And of thir vain contest appeer'd no end."),
 # ---------------- Livro 10 ----------------
 (10,1,'O Filho desce a julgar — e os veste de misericórdia','do trono celeste ao Jardim, ao cair da tarde','meio',
  "O Pai transfere todo o juízo ao Filho, que desce ao Éden para sentenciar Adão e Eva. Mesmo ao pronunciar a maldição, tempera a justiça com misericórdia: assume a forma de servo e cobre a nudez do casal com peles, e a nudez interior com sua veste de justiça.",
  "O juízo que não esmaga, mas cobre e levanta, é uma filosofia de viver — um passo de autoconhecimento sobre como a misericórdia rompe a cápsula da pura culpa. Experimenta-se ser julgado e, ao mesmo tempo, acolhido.",
  "But whom send I to judge them? whom but thee","Araying cover'd from his Fathers sight."),
 (10,2,'Pecado e Morte erguem a ponte do Inferno à Terra','das portas do Inferno, sobre o Caos, ao mundo caído','memoria',
  "Sentindo por simpatia secreta o triunfo de Satã, Pecado e Morte saem das portas do Inferno e, com a maça petrificante da Morte, consolidam o Caos numa imensa calçada. Erguem assim uma ponte prodigiosa que une o Inferno à Terra agora indefesa, entregue à Morte.",
  "Imagem arquitetônica do mal que se torna estrada livre — a ponte 'lisa, fácil, sem obstáculo, descendo ao Inferno' fixa-se na memória como a materialização visível das consequências do pecado.",
  "Meanwhile ere thus was sin'd and judg'd on Earth,","And scourg'd with many a stroak th' indignant waves."),
 (10,3,'Aplauso virado em silvo: "a dismal universal hiss"','Pandæmonium, o salão de Satã e o campo do Inferno','intuicao',
  "Satã retorna a Pandæmonium e jacta-se de seu triunfo, esperando aclamação. Em vez de aplauso, ouve um silvo universal de escárnio: ele e toda a sua hoste são subitamente transformados em serpentes, e seu discurso de glória converte-se em sibilo.",
  "O contraste súbito — orgulho no auge, depois a queda em serpente — é sentido antes de raciocinado: a punição 'na forma em que pecou' atinge como vertigem moral. Experimenta-se o ridículo e o horror que a soberba capsulada atrai sobre si.",
  "So having said, a while he stood, expecting","As in thir crime. Thus was th' applause they meant,"),
 (10,4,'Solilóquio do desespero: "O fleeting joys of Paradise"','o chão frio do Jardim, na noite após a queda','sinceridade',
  "Estendido no chão frio através da noite, Adão lamenta em voz alta. Acusa-se como fonte da maldição que recairá sobre toda a posteridade, deseja nunca ter nascido ou ser reduzido ao nada, e debate consigo a possibilidade de uma morte que talvez não acabe, afundando 'do fundo a mais fundo'.",
  "Verdade humana crua e dilema moral nu: a consciência levada ao 'abismo de medos'. Adão fechado em sua própria culpa é a imagem máxima do eu fechado — vive-se por dentro o peso de carregar sozinho a responsabilidade.",
  "O fleeting joyes","Thus Adam to himself lamented loud"),
 (10,5,'Eva toma sobre si toda a culpa: "me, me only"','aos pés de Adão, depois no lugar do juízo, em prece','sinceridade',
  "Repelida com dureza, Eva cai aos pés de Adão e suplica, oferecendo-se para levar toda a sentença sobre sua cabeça — chegando a propor a morte em seu lugar. Sua humildade amolece Adão, que abandona a ira; juntos rejeitam o suicídio e o desespero e voltam-se ao lugar do juízo para confessar e orar.",
  "O gesto de Eva — assumir a culpa do outro, oferecer-se em seu lugar — rompe a cápsula individual: do amor sincero nasce a reconciliação e, dela, o paraíso interior da prece compartilhada. Vive-se a virada da acusação à comiseração.",
  "Forsake me not thus, Adam, witness Heav'n","Before him reverent, and both confess'd"),
 # ---------------- Livro 11 ----------------
 (11,1,'As preces que sobem ao Céu e a sentença de exílio','do oratório na Terra ao trono do Pai no Céu','meio',
  "As orações contritas de Adão e Eva, movidas pela Graça Preveniente, sobem ao Céu, onde o Filho as apresenta e intercede como advogado. O Pai aceita o pedido, mas decreta que o casal deve deixar o Paraíso, fazendo da Morte o remédio final, e envia Michael para executar a sentença.",
  "A oração é o primeiro passo concreto rumo ao autoconhecimento e a uma filosofia de viver: o eu fechado se rompe ao admitir que algo 'deve subir ao Céu'. A intercessão desenha o caminho do meio entre culpa e redenção.",
  "Thus they in lowliest plight repentant stood","And send him from the Garden forth to Till"),
 (11,2,'"Must I leave thee, Paradise?" — o lamento de Eva','a chegada de Michael e o recanto de Eva','sinceridade',
  "Michael anuncia a sentença de exílio; Adão fica fulminado de dor e Eva, escondida, prorrompe em lamento por ter de deixar suas flores, o caramanchão nupcial e o solo natal. O Anjo a repreende com brandura, e Adão, recuperando-se, submete-se à decisão divina contra a qual a oração de nada serviria.",
  "É a verdade humana crua diante da perda: Eva nomeia uma a uma as flores que criou e Adão confessa o que mais o aflige — ser apartado da face de Deus. O dilema entre apego e resignação expõe o coração sem disfarce.",
  "Eve, now expect great tidings, which perhaps","Recovering, and his scatterd spirits returnd,"),
 (11,3,'A primeira Morte: Caim e Abel — "have I now seen death?"','no alto da colina, na visão profética de Michael','intuicao',
  "Adão contempla, na primeira visão do futuro, o campo onde dois irmãos sacrificam; o fogo do Céu aceita a oferta do pastor humilde, mas não a do lavrador, que, enraivecido, esmaga o irmão com uma pedra. Diante do primeiro morto, Adão pergunta horrorizado se é assim que retornará ao pó.",
  "Adão sente a Morte como experiência vívida antes de raciociná-la — 'horrível de pensar, quão horrível de sentir!'. O choque vicário do primeiro assassinato rompe a cápsula do eu pela percepção imediata, não pela explicação.",
  "His eyes he op'nd, and beheld a field,","Groand out his Soul with gushing bloud effus'd."),
 (11,4,'O Lazar-house: a multidão das doenças e o pranto de Adão','na visão de Michael, diante do hospital dos enfermos','memoria',
  "Michael mostra a Adão um lugar sombrio e fétido onde jazem todas as enfermidades — convulsões, febres, melancolia, pestilência — com a Morte triunfante brandindo o dardo sobre os doentes que a invocam como derradeira esperança. Adão chora ante a degradação da imagem de Deus no homem.",
  "O Lazar-house é imagem viva e indelével — o catálogo dos males a guardar — que faz até 'coração de rocha' não poder olhar de olhos secos. Pela compaixão vicária, Adão sai da própria cápsula e chora pela humanidade inteira.",
  "Some, as thou saw'st, by violent stroke shall die,","And scarce recovering words his plaint renew'd."),
 (11,5,'Dos prazeres ao Dilúvio: "judge not what is best by pleasure"','as visões da intemperança, da violência e do Dilúvio','meio',
  "Adão vê a planície da intemperança, onde os homens cedem às belas ateias, e Michael adverte que prazer não é medida do bem; seguem-se a violência dos gigantes, o arrebatamento de Enoque, e enfim Noé que, pregando em vão, constrói a Arca enquanto o Dilúvio submerge o mundo. O Arco-íris sela a nova Aliança.",
  "Michael ensina o discernimento — 'não julgues o que é melhor pelo prazer' — convertendo a sucessão de visões num exercício de temperança e autoconhecimento. O único justo num mundo perverso mostra o caminho do meio que preserva a vida em meio à ruína.",
  "He lookd and saw a spacious Plaine, whereon","And scarce to th' Angel utterdst thus thy plaint."),
 # ---------------- Livro 12 ----------------
 (12,1,'Nimrod e a tirania de Babel — até o chamado de Abraão','a segunda parte da visão de Michael','memoria',
  "Michael mostra como, da paz patriarcal, ergue-se um homem de coração ambicioso que arroga 'domínio imerecido' sobre os irmãos — o caçador de homens — e constrói a Torre de Babel, punida com a confusão das línguas. Da decadência das nações, Deus escolhe um só homem fiel, Abraão, que deixa Ur rumo a uma terra desconhecida.",
  "A imagem do 'caçador de homens' e da torre que se desfaz em balbúrdia é o retrato vivo da origem da dominação sobre o semelhante — o eu fechado projetado em estrutura política, contraste do paraíso interior que virá.",
  "Under paternal rule; till one shall rise","With God, who call'd him, in a land unknown."),
 (12,2,'A "semente" prometida: "shall bruise the Serpent\'s head"','a profecia do Redentor e a felix culpa','sinceridade',
  "Michael revela que pela 'semente' de Abraão se entende o grande libertador que esmagará a cabeça da Serpente, e adverte Adão a não imaginar a luta como um duelo de feridas: o Salvador vence não destruindo Satã, mas suas obras, cumprindo a Lei por amor e sofrendo a morte devida — convertendo a própria morte dos redimidos num 'doce trânsito para a vida imortal'.",
  "Expõe-se a verdade mais crua — a culpa que pesa sobre Adão — convertida em ocasião de um bem maior, sem mascarar o custo do resgate. A sinceridade está em encarar que a redenção não apaga o pecado, mas o reordena.",
  "This ponder, that all Nations of the Earth","A gentle wafting to immortal Life."),
 (12,3,'"A paradise within thee, happier far" — acrescenta o Amor','a última fala de Michael, no alto da especulação','meio',
  "Michael declara que Adão, tendo aprendido a obedecer e a amar, atingiu 'a soma da sabedoria', e que de nada vale conhecer todos os astros sem acrescentar obras, fé, virtude, paciência, temperança e, sobretudo, o Amor, 'que pelo nome a vir se chamará Caridade, a alma de todo o resto'. Então não relutará em deixar o Paraíso exterior, pois possuirá 'um paraíso interior, muito mais feliz'.",
  "Este é o desfecho exato do método: o autoconhecimento culmina numa filosofia do viver em que a Caridade, alma de todas as virtudes, abre a cápsula individual e instala o paraíso interior — resolvendo a through-line do 'myself am Hell' no paraíso de dentro.",
  "To whom thus also th' Angel last repli'd:","A Paradise within thee, happier farr."),
 (12,4,'A Expulsão: "hand in hand... their solitary way"','o final do poema — a espada flamejante e a saída do Éden','intuicao',
  "Michael ordena descerem do alto, pois a espada flamejante já ondeia em sinal de partida; os Querubins descem como névoa e a espada de Deus queima feroz como um cometa. O anjo toma os 'pais hesitantes' pela mão e os conduz ao Portão Oriental; eles, olhando para trás o Paraíso vedado, enxugam algumas lágrimas e seguem, de mãos dadas, com passos lentos e errantes, seu caminho solitário.",
  "É a imagem afetiva suprema, sentida antes de qualquer raciocínio: o mundo 'todo diante deles', a Providência por guia, o casal saindo não para o nada, mas para a errância humana que carrega já o paraíso interior. A intuição capta a resolução serena da through-line no 'hand in hand'.",
  "Let us descend now therefore from this top","Through Eden took thir solitarie way."),
]


def anchor_regex(anchor: str):
    parts = [re.escape(tok) for tok in anchor.split()]
    return re.compile(r"\s+".join(parts))


def matches(text: str, anchor: str) -> bool:
    return anchor_regex(anchor).search(text) is not None


def normalize_anchor(text: str, anchor: str):
    """Retorna a versao da ancora que casa no texto (crua ou sem aspas ao redor), ou None."""
    cands = [anchor]
    stripped = anchor.strip().strip('"').strip('“”').strip()
    if stripped != anchor:
        cands.append(stripped)
    for c in cands:
        if c and matches(text, c):
            return c
    return None


def main() -> int:
    assert len(SCENES) == 55, f"esperado 55 cenas, há {len(SCENES)}"
    CAPDIR.mkdir(exist_ok=True)

    # 1) copia os 12 Livros para PL-capitulos/ + index
    cap_index = {"obra": "Paradise Lost", "autor": "John Milton", "capitulos": []}
    book_capfile = {}
    for b in range(1, 13):
        src = CHAPTERS / BOOK_FILE[b]
        fname = f"{b:02d}_cap-{b:02d}_livro-{b:02d}.md"
        shutil.copyfile(src, CAPDIR / fname)
        book_capfile[b] = fname
        cap_index["capitulos"].append({"arquivo": fname, "cap_label": f"{b} — Livro {b}", "cap": b})
    (CAPDIR / "_capitulos_index.json").write_text(
        json.dumps(cap_index, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2) monta manifest + anchors com QC
    book_text = {b: (CHAPTERS / BOOK_FILE[b]).read_text(encoding="utf-8") for b in range(1, 13)}
    cenas, anchors, problems = [], {}, []
    seq = 0
    for (b, cl, tit, loc, pil, res, jus, ai, af) in SCENES:
        seq += 1
        txt = book_text[b]
        nai, naf = normalize_anchor(txt, ai), normalize_anchor(txt, af)
        if nai is None:
            problems.append(f"seq {seq} (Livro {b}) INICIO sem match: {ai!r}")
        if naf is None:
            problems.append(f"seq {seq} (Livro {b}) FIM sem match: {af!r}")
        cenas.append({
            "seq_global": seq, "cap": b, "cena_local": cl, "titulo": tit,
            "localizacao": loc, "resumo": res, "pilar_foco": pil,
            "justificativa_cof": jus, "source_chapter": book_capfile[b],
        })
        anchors[str(seq)] = {"inicio": nai or ai, "fim": naf or af}

    manifest = {
        "obra": "Paradise Lost", "autor": "John Milton", "slug": "paradise-lost",
        "idioma_obra": "en", "output_language": "pt-BR",
        "nota_idioma": "Narração em pt-BR citando o verso em inglês (decisão do projeto).",
        "width": 2, "total_cenas": len(cenas), "cenas": cenas,
    }
    (PROJ / "_cenas_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (PROJ / "_anchors.json").write_text(
        json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8")

    # distribuicao de pilares
    from collections import Counter
    dist = Counter(c["pilar_foco"] for c in cenas)
    print(f"OK: {len(cenas)} cenas, 12 Livros em {CAPDIR.name}/")
    print("Pilares:", dict(dist))
    if problems:
        print(f"\n*** {len(problems)} ÂNCORAS SEM MATCH (corrigir) ***")
        for p in problems:
            print("  -", p)
        return 2
    print("\nTodas as 110 âncoras casaram no texto real. ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
