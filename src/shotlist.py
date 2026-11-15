"""Episode 01 - The Promise: timestamped shot list locked to the master narration.

Times are seconds in the narration (190.85 s). Cuts sit on detected pauses
(silencedetect -33 dB / 0.18 s) so every shot follows a phrase of the grandmother.
Frame f covers t=(f-1)/30.  Transcript lines are Whisper-small (sherpa-onnx) output,
lightly cleaned; they are reference only and never rendered."""
FPS = 30
DURATION = 190.85
LAST_FRAME = 5726


def F(t):
    return int(round(t * FPS)) + 1


#   id, t0, t1, set, mood, title, narration (Arabic, spoken over the shot)
SHOTS = [
    # 01 THE TWO SISTERS
    ('S01', 0.00, 5.24, 'street', 'warm_morning', 'Crane down over the rooftops to the family house', 'تعالوا يمي يا ولادي، خلي أحكيلكم حكاية صارت من زمان'),
    ('S02', 5.24, 10.55, 'house', 'interior_warm', 'Living room: the sisters playing on the carpet', 'حكاية أختين صغار، كانوا يحبون بعض حب ما ينحكى'),
    ('S03', 10.55, 13.95, 'house', 'interior_warm', 'Close-up Hind (5) with her white rabbit', 'وحدة اسمها هند، عمرها خمس سنين'),
    ('S04', 13.95, 17.66, 'house', 'interior_warm', 'Close-up Huda (7), gentle smile', 'والثانية اسمها هدى، عمرها سبع سنين'),
    ('S05', 17.66, 21.23, 'house', 'interior_warm', 'Huda crosses the room, Hind follows', 'هدى كانت الأخت الكبيرة، ووين ما تروح هند تلحقها'),
    ('S06', 21.23, 23.98, 'house', 'interior_warm', 'Ball toss, laughter', 'يلعبن سوى، يضحكن سوى'),
    ('S07', 23.98, 27.15, 'house', 'interior_warm', 'Playful tug over the toy car, Hind pouts', 'وحتى من يتعاركن'),
    ('S08', 27.15, 29.84, 'house', 'interior_warm', 'Reconciliation hug', 'بعد شوية يرجعن يحبن بعض'),
    ('S09', 29.84, 33.87, 'house', 'interior_warm', 'Kitchen: mother cooking, steam', 'وبيوم من الأيام، أمهم كانت تريد تطبخ الغدا'),
    ('S10', 33.87, 37.76, 'house', 'interior_warm', 'Empty vegetable basket', 'بس احتاجت خضروات'),
    ('S11', 37.76, 41.70, 'house', 'interior_warm', 'Mother calls Huda and gives her money', 'نادت هدى وقالت لها: يمّا روحي للدكان وجيبيلي شوية خضروات'),
    # 02 THE PROMISE
    ('S12', 41.70, 46.80, 'street', 'warm_morning', 'Out of the front door, Hind follows with her rabbit', 'أخذت هدى الفلوس وطلعت، وهند وراها شايلة أرنوبها الصغير'),
    ('S13', 46.80, 51.75, 'street', 'warm_morning', 'Tracking: the sisters walk the neighbourhood', 'الدكان كان قريب، بس لازم يعبرون شارع حتى يوصلون له'),
    ('S14', 51.75, 56.41, 'street', 'warm_noon', 'Wide: shop across the road, they reach the curb', 'ولما وصلوا للرصيف، هدى مسكت إيد أختها'),
    ('S15', 56.41, 60.09, 'street', 'warm_noon', 'Huda points at the passing cars', 'وقالت لها: هند، إنتِ لا تجين، أخاف سيارة تدعسك'),
    ('S16', 60.09, 63.30, 'street', 'warm_noon', 'Huda: stay here, I will be back', 'ابقي هنا، أنا أشتري وأرجع بسرعة'),
    ('S17', 63.30, 65.90, 'street', 'warm_noon', 'Hind disappointed', 'هند ما كانت تريد تبقى وحدها'),
    ('S18', 65.90, 69.13, 'street', 'warm_noon', 'Huda smiles and offers her little finger', 'فهدى ابتسمت ومدّت إصبعها الصغير'),
    ('S19', 69.13, 73.27, 'street', 'warm_noon', 'MACRO: the pinky promise', 'وشبكن أصابعهن، وعد صغير بين أختين'),
    # 03 THE ACCIDENT
    ('S20', 73.27, 76.34, 'street', 'warm_noon', 'Huda crosses carefully; Hind stays on the sidewalk', 'راحت هدى، وبقت هند تنتظرها'),
    ('S21', 76.34, 79.59, 'street', 'warm_noon', 'Inside the shop: tomatoes into the bag', 'وبعد شوية شافتها طالعة من الدكان'),
    ('S22', 79.59, 83.73, 'street', 'warm_noon', 'Huda exits with the bag and waves', 'وبإيدها جنطة الخضروات، لوّحت هدى لأختها'),
    ('S23', 83.73, 86.42, 'street', 'warm_noon', 'Hind waves back, laughing', 'وهند لوّحت لها وهي تضحك'),
    ('S24', 86.42, 88.14, 'street', 'tense', 'A van passes and blocks the view', 'بس فجأة يا ولادي'),
    ('S25', 88.14, 90.30, 'street', 'tense', "Hind's eyes widen at the screech of brakes", 'انسمع صوت فرامل قوي'),
    ('S26', 90.30, 92.17, 'street', 'tense', 'People rush, low angle', 'وصوت ناس تصيح'),
    ('S27', 92.17, 95.49, 'street', 'tense', 'The rabbit falls from her hand', 'هند تجمدت، وطاح أرنوبها من إيدها'),
    ('S28', 95.49, 98.82, 'street', 'tense', 'The crowd gathers, seen from Hind’s height', 'الناس تجمعوا بالشارع'),
    ('S29', 98.82, 100.97, 'street', 'tense', 'A woman cries out', 'ووحدة صاحت: سيارة دعست بنية'),
    ('S30', 100.97, 105.19, 'street', 'cool_after', 'Hind tries to see; legs and backs block her', 'هند حاولت تشوف، بس الناس كانوا حاجبين الطريق'),
    ('S31', 105.19, 108.79, 'street', 'cool_after', 'Hind, inner voice: no, not Huda', 'قالت بينها وبين نفسها: لا، أكيد مو هدى'),
    ('S32', 108.79, 111.57, 'street', 'cool_after', 'Over-shoulder: she promised to come back', 'هدى وعدتني ترجع'),
    ('S33', 111.57, 114.55, 'street', 'cool_after', 'Ground level: a tomato rolls slowly', 'وفجأة شافت حبة طماطة تتدحرج بالشارع'),
    ('S34', 114.55, 117.18, 'street', 'cool_after', 'Rack focus: the torn vegetable bag', 'وراها جنطة خضروات ممزقة'),
    ('S35', 117.18, 120.08, 'street', 'cool_after', 'Extreme close-up: Hind’s frightened eyes', 'نفس الجنطة اللي كانت بإيد هدى'),
    # 04 WAITING
    ('S36', 120.08, 123.62, 'street', 'cool_after', 'The ambulance arrives, lights flashing', 'وصل الإسعاف وأخذوا البنية للمستشفى'),
    ('S37', 123.62, 126.51, 'street', 'cool_after', 'Ambulance leaves, crowd disperses', 'وهند بقت تنتظر'),
    ('S38', 126.51, 129.78, 'street', 'late_cool', 'Time passes: long shadows, emptying street', 'دقيقة، خمس دقائق، ووقت طويل مر'),
    ('S39', 129.78, 131.58, 'street', 'late_cool', 'Hope turns to fear', 'بس هدى ما رجعت'),
    # 05 THE EMPTY HOUSE
    ('S40', 131.58, 134.47, 'street', 'late_cool', 'Hind runs home', 'ركضت هند للبيت'),
    ('S41', 134.47, 136.97, 'house', 'interior_cool', 'The door opens: Hind in the doorway', 'فتحت الباب'),
    ('S42', 136.97, 138.88, 'house', 'interior_cool', 'Searching the rooms, calling', 'ودورت على أمها بكل الغرف'),
    ('S43', 138.88, 143.08, 'house', 'interior_cool', 'Kitchen: lunch left unfinished', 'بس البيت كان فارغ، حتى الغدا اللي كانت أمها تطبخه بقى ما كمل'),
    ('S44', 143.08, 146.19, 'street', 'late_cool', 'At the front door: the neighbour approaches', 'طلعت هند للباب وشافت جارتهم'),
    ('S45', 146.19, 150.50, 'street', 'late_cool', 'The neighbour kneels and holds her hands', 'قربت منها الجارة ومسكت إيديها الصغار'),
    ('S46', 150.50, 155.68, 'street', 'late_cool', 'Gently, the neighbour tells her', 'وقالت لها: هند يمّا، أختچ هدى دعستها سيارة وأخذوها للمستشفى'),
    ('S47', 155.68, 160.37, 'street', 'late_cool', 'Hind stares, unable to believe', 'هند بقت تباوع بوجه الجارة وكأنها ما صدقت الكلام'),
    ('S48', 160.37, 163.18, 'house', 'interior_cool', 'She runs into Huda’s room', 'وبعدين ركضت لغرفة أختها'),
    ('S49', 163.18, 166.68, 'house', 'interior_cool', 'She hugs Huda’s pillow and cries', 'حضنت مخدتها وصارت تبچي'),
    ('S50', 166.68, 170.93, 'house', 'interior_cool', 'Close-up: tears - "you promised to come back"', 'وتقول: هدى، إنتِ وعدتيني ترجعين، ليش ما رجعتي؟'),
    # 06 THE CLIFFHANGER
    ('S51', 170.93, 174.65, 'hospital', 'hospital', 'Hospital: Huda asleep, mother at her side', 'وبذاك الوقت يا ولادي، هدى كانت بالمستشفى'),
    ('S52', 174.65, 178.32, 'hospital', 'hospital', 'Mother holds Huda’s small hand', 'وأمها قاعدة يمها، تنتظرها تفتح عيونها'),
    ('S53', 178.32, 183.47, 'house', 'dusk', 'Hind alone at the doorway with her rabbit', 'أما هند فبقت بالبيت، تنتظر صوت خطوات أختها'),
    ('S54', 183.47, 186.99, 'hospital', 'hospital', 'Huda’s little finger on the blanket', 'بس ذاك اليوم ما انتهى مثل ما تمنت هند'),
    ('S55', 186.99, 190.85, 'house', 'dusk', 'Hind’s lonely pinky; pull back; fade to black', 'وبعدها بدت أطول ثلاث أيام بحياتها'),
]


def frames(shot):
    _, t0, t1 = shot[:3]
    f0 = F(t0)
    f1 = LAST_FRAME if t1 >= DURATION - 1e-6 else F(t1) - 1
    return f0, f1


def scene_map_md():
    rows = ['| Shot | Time (s) | Frames | Set | Light | Picture | Narration |', '|---|---|---|---|---|---|---|']
    for s in SHOTS:
        f0, f1 = frames(s)
        rows.append(f'| {s[0]} | {s[1]:.2f}–{s[2]:.2f} | {f0}–{f1} | {s[3]} | {s[4]} | {s[5]} | {s[6]} |')
    return '\n'.join(rows)


if __name__ == '__main__':
    print(scene_map_md())
