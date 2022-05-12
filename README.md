
Add this lines to your `settings.env` file and replace the token with your bot token for local development.

```
[DEVELOPMENT]
APP_NAME=TESTING
TOKEN=very_secret_token
MONGO_HOST=host
MONGO_USER=user
MONGO_PASS=very_secrte_password
MONGO_BASE=base
```

deploy test branch
```
git push heroku test-deploy:main
```

deploy main branch 
```


```

**In Chat Group Bot should have ADMIN rights**

##Release Notes 
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
- add new commands: `/countries_all`, `/entertainment, `/meetup`, `/school`, `/vaccination` , `/germany_asyl_all`.
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

- Searching for terms is case-insensetive.