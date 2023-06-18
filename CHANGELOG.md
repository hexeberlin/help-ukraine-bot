### 20230618
- update `/no_ads`

### 20230613
- fix `/university`
- update `/medical`

### 20230612
- update `/legal`
- update and rename `/uni` to `/university`
- update Readme

### 20230611
- add `/lost_passport`

### 20230608
- update `/transport`, `/deutsch`
- update `/disabled` and rename to `/handicap`
- add `/diplom`

### 20230530
- update `/transport`, `/return_to_ukraine`
- add `/deutschlandticket`

### 20230501
- update `/wbs`, `/passport`, `/furniture`
- remove `/meetup`

### 20230410
- create `CHANGELOG.md`
- update `README.md`
- add `.pylintrc`
- update `/education`, `/general_information`, `/cities`, `/passport`
- remove `/handbook`, `/adaptation`
- add new `/apartment_approval`

### 20230401
- update `/translators`, `/transport`, `/accomodation`, `/entertainment`
- add new `/qrcode`, remove `/berlinpass`

### 20230215
- update `/translators`, `/transport`, `/simcards`, `/passport`
- add new `/furniture`
- Use # instead of / before command name

### 20230201
- update `/vaccination`, `/jobs`
- add new `/passport`
- print command name before response

### 20230125
- update `/transport`, `/apartments`, `/medical`, `/jobs`, `/psychological`

### 20221229
- update `/transport`, `/beauty`, `/no_ads`, `/jobs`, `/psychological`
- add Wiesbaden to `/cities`

### 20221124
- update `/volunteer`, `/transport`, `/simcards`, `/jobs`, `/legal`, `/pregnant`, `/uni`, `/psychological`, `/beauty`
- remove duplicates from `/animals`, `/accomodation`
- remove commands `/taxis`, `/moving`
- combine both commands for disabled
- mention author of `/return_to_ukraine`

### 20221101
- update `/cities_all`, `/countries_all`, `/animals`, `/berlinpass`, `/medical`
- add `/return_to_ukraine`

### 20221028
- update `/translators`, `/cities`, `/freestuff`
- remove `hryvnia`

### 20221012
- update `/job_center_calc`, `/jobs`, `/psychological`, `/rundfunk`

### 20220915
- update `/hryvnia`, `/medical`, `/cities`

### 20220831
- update `/transport`, `/animals`
- remove `/euro_9`

### 20220815
- update `/photo`, `/leave`
- remove `/banking`
- add `/job_center_calc`, `/search`

### 20220812
- update `/berlinpass`, `/photo`

### 20220810
- add commands `/apartments`, `/berlinpass`
- update `/countries`, `/cities`
- remove unused lines
- change description to russian

### 20220729
- add command `/leave`
- update `/socialhelp`, `/handbook`, `euro_9`, `/entertainment`, `/beschwerde`, `/beauty`, `/banking`, `/legal`, `/simcards`, `/vaccination`
- remove `/german_asyl`

### 20220720
- add commands `/kindergeld`, `/beschwerde`, `/no_ads`, `/schufa`, `/wbs`, `/rundfunk`, `/euro_9`
- update `/food`, `/kids-with-special-needs`, `/transport`, `/minors`, `/entertainment`, `/beauty`, `/general_information`, `/freestuff`, `/children_lessons`, `/hryvnia`, `/translators`, `/jobs`, `/psychological`
- rename `/freestuff` to `/free_stuff`
- remove `/humanitarian`
- update cities chats:
  - add Halle (Saale)
  - add Frankfurt Oder
  - update Köln

### 20220512
- add command `/moving`, `/pregnant`
- update cities chats:
  - add Castrop-Rauxel 
  - add Helmstedt 
  - update Rostock 
  - update Wuppertal 
- update evacuation_cities command 
- update `/medical` command
- update `/deutsch` command
- update `/humanitarian`
- update `/disabled` command
- update `/accomodation` command
- fix translators "Чат переводчиков"
### 20220330:
- add commands: `/simcards`, `/photo`, `/transport`
- update commands: `/jobs`, `/food`
### 20220329:
- delete commands before parsing results
- update `/jobs` command
- refactoring
### 20220328:
- add `/food` command
- update `/cities` chat
- update `/jobs`
- update `translators`

### 20220327:
- add new commands: `/countries_all`, `/entertainment`, `/meetup`, `/school`, `/vaccination` , `/germany_asyl_all`.
- command `/countries `now has the same behaviour as command `/cities`.
- commands `/countries`, `/cities`, `/meetup` and `/germany_asyl` can work with parameters. If a name has german umlauts (*ä*, *ö*, *ü*), you can use *ä*, *ö*, *ü* OR *ä*->*a*, *ö*->*o*, *ü*->*u* OR *ä*->*ae*, *ö*-*oe*, *ü*-*ue*. For example, you can search for **Köln** as *Köln*, *Koln* or *Koeln*. Also you can now search **Frankfurt am Main** as *fam*.
- updated commands with new information: `/accomodation`, `/cities`, `/counties`, `/taxis`, `/medical`, `/psychological`, `/dentist` , `/humanitarian`.
- this commands were rewritten: `/psychological`, `/legal`, `/accomodation`. 
- instead of `/vet` command please use `/animals`, instead `/germany_domestic` use `/germany_asyl`.
- existing paramters for `/germany_asyl` (searching for terms in brackets):
  - Mecklenburg-Vorpommern(Mecklenburg-Vorpommern, MV, Мекленбург, Mecklenburg)
  - Niedersachsen(Niedersachsen, NI, Нижняя_саксония, Нижняя-саксония)
  - Sachsen-Anhalt(Sachsen-Anhalt, Саксония, ST, Sachsen)
  - Rheinland-Pfalz(Rheinland-Pfalz, RP,Рейнланд_пфальц, Рейнланд-пфальц,Rheinland)
  - Nordrhein-Westfalen(Nordrhein-Westfalen, NW, NRW, Рейн_вестфалия,рейн-вестфалия,  Nordrhein).
- Searching for terms is case-insensetive
