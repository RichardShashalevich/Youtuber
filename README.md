# YouTube analīzes rīks

## Projekta uzdevums
Šī programma automatizē YouTube videoklipu meklēšanu un analīzi, pamatojoties uz lietotāja ievadīto pieprasījumu. Tā:
- Iegūst līdz `MAX_RESULTS` videoklipus noteiktā datumu intervālā.
- Filtrē kanālus pēc abonentu skaita (`MIN_SUBSCRIBERS` līdz `MAX_SUBSCRIBERS`).
- Apkopo statistiku (skatījumi, patīk, viralitāte, iesaistīšanās).
- Saglabā labākos rezultātus CSV formātā un izvada konsolē kopsavilkumu.
- Identificē visbiežāk lietotos vārdus videoklipu virsrakstos un aprakstos, izslēdzot pieturzīmes un specifiskus stop-vārdus.
This programs can be usefull for small Youtube chanels to explore the eye-catching topics and gather catchy keywords in titles to produce content and gather more audiance.
## Izmantotās bibliotēkas
- `google-api-python-client`: piekļuve YouTube Data API v3 meklēšanai un datu iegūšanai.  
- `pandas`: datu sakārtošana tabulās un CSV failu ģenerēšana.  
- Standarta bibliotēkas moduļi: `time`, `datetime`, `string`.

## Pielāgotās datu struktūras
- **HashMap**  
  Vienkārša haštabula ar ķēdveida sadalīšanas (chaining) kolīzijas risināšanu.  
  - `put(key, value)`, `get(key)`, `remove(key)`  
  - `__contains__`, `__len__`, iteratori: `keys()`, `values()`, `items()`  
  - `most_common(n)`: atgriež top-n atslēgu-un-vērtību pārus, sakārtotus pēc vērtības dilstošā secībā.
- **YouTubeAnalyzer klase**
    Apraksta programmas galveno analīzes plūsmu un CSV ģenerēšanu:
    - `__init__(api_key, query)`  
    Iniciē YouTube Data API klientu, saglabā meklēšanas vaicājumu un inicializē kanālu kešatmiņu.
    - `get_date_range()`  
    Ģenerē sākuma un beigu datumus, balstoties uz `TIME_FILTER` iestatījumiem (gads, mēnesis, sezona, pēdējās dienas vai pielāgots).
    - `get_channel_subscribers(channel_id)` / `calculate_channel_subscribers(channel_id)`  
    Iegūst kanāla abonentu skaitu no API un kešo to, lai izvairītos no liekiem pieprasījumiem.
    - `search_request(start_date, end_date, page_token)`  
    Veic video meklēšanu, apstrādājot lappušu pārlūkošanu (`nextPageToken`) un ievērojot `MAX_RESULTS` limitu.
    - `process_video_item(item)`  
    Apstrādā atsevišķu video rezultātu: iegūst statistiku, filtrē pēc abonentu skaita un sagatavo ierakstu.
    - `get_videos()`  
    Savāc visus atbilstošos video ierakstus, līdz sasniegts `MAX_RESULTS` vai nav vairāk lapu.
    - `analyze_and_save(videos)`  
    Pārvērš datus `pandas.DataFrame`, ģenerē trīs CSV failus (`top_views.csv`, `top_virality.csv`, `top_engagement.csv`), saglabā pilnu rezultātu `youtube_analysis.csv`, kā arī vārdu skaita CSV (`title_word_counts.csv`, `description_word_counts.csv`), un izvada konsolē galvenos kopsavilkumus.
    - `run()`  
    Vienkārši izsauc `get_videos()` un `analyze_and_save()`, lai palaistu pilnu analīzi.


## Failu struktūra
- `main.py`: galvenais skripts, kas ielādē YouTubeAnalyzer klasi un palaiž analīzi  
- `YouTubeAnalyzer.py`: satur `YouTubeAnalyzer` klasi ar visu analīzes loģiku  
- `word_analyser.py`: definē `HashMap` un `count_words` funkciju  
- `API_KEY.py`: glabā jūsu YouTube Data API atslēgu  

## Lietošana

1. **Konfigurēšana**  
   - Norādi savu API atslēgu `API_KEY.py` failā.  
   - Pielāgo konstantus `main.py`:
     - `MAX_RESULTS`, `LANGUAGE`, `MIN_SUBSCRIBERS`, `MAX_SUBSCRIBERS`.  
     - `TIME_FILTER`: gads, mēnesis, sezona, pēdējās dienas vai pielāgots datumu intervāls.
     
     Piemēri:
     ```python
     # main.py — vienkārša iestatījumu maiņa
     MAX_RESULTS      = 100
     LANGUAGE         = "en"
     MIN_SUBSCRIBERS  = 5000
     MAX_SUBSCRIBERS  = 50000
     TIME_FILTER      = {'last_days': 30}
     ```
     ```python
     # main.py — pielāgots datumu intervāls
     TIME_FILTER = {
         'custom_range': {
             'start': '2024-01-01',
             'end':   '2024-06-30'
         }
     }
     ```

2. **Skripta palaišana**  
   ```bash
   python main.py
   ```
   - Ievadi meklēšanas vaicājumu, kad tiek prasīts.

3. **Rezultāti**  
   - `youtube_analysis.csv`: visa apkopotā informācija  
   - `top_views.csv`, `top_virality.csv`, `top_engagement.csv`: sakārtotas atsevišķas tabulas  
   - `title_word_counts.csv`, `description_word_counts.csv`: pilnas vārdu skaita tabulas  
   - Konsolē tiek izvadīts:  
     - Top-10 vārdus virsrakstos un aprakstos.

4. **Paplašināšana**  
   - Maini `TIME_FILTER`, lai analizētu citus laika periodus.  
   - Papildini `word_analyser.py`, lai atjauninātu stop-vārdus.  
   - Palielini `MAX_RESULTS`, ja nepieciešams analizēt vairāk rezultātu (lappušu pārlūkošana nodrošina analīzi līdz API limitam).
