import discord
import os
from discord.ext import commands
import requests
from dictionary import dictProvince
from dictionary import dictRegion
from dictionary import mapHr
from dictionary import dictP
from dictionary import dictCountry
from datetime import date
from datetime import datetime
from datetime import timedelta

client = commands.Bot(command_prefix="covid ")
client.remove_command('help')

dateCurrent = str(date.today().day) + '-'+str(date.today().month) + "-" + str(date.today().year) 


def dayBack(dateNow):
  dateCurrent = dateNow.split('-')
  today = date(int(dateCurrent[2]),int(dateCurrent[1]),int(dateCurrent[0]))
  yesterday = today - timedelta(days = 1)
  return str(yesterday.day)+"-"+str(yesterday.month)+"-"+str(yesterday.year)

if datetime.now().hour < 22:
  dateCurrent = dayBack(dateCurrent)


@client.command()
async def help(ctx):
  embed1 = discord.Embed(title="Covid Help",description=":robot: These are the available commands for CovidInfoBot :robot:\nDefault region is Canada and default date is today\nUse dashes whenever spaces are needed for country names!")
  embed1.set_footer(text=str("Covid Info"))
  embed1.add_field(name="covid advice(region)", value="Gives safety advice for a region and its nearby region",inline="true")
  embed1.add_field(name="covid update(region)", value="Gives the time that the data was last updated",inline="true")
  embed1.add_field(name="covid summary", value="Gives a summary of covid statistics worldwide",inline="true")
  embed1.add_field(name="covid country(country, date)", value="Gives covid statistics for a given country",inline="true")
  embed1.add_field(name="covid cases(region, date)", value="Gives covid statistics for a given region in canada",inline="true")
  embed1.add_field(name = 'covid general(region, date)', value= 'Gives general covid statistics for a province/health region in Canada. ',inline = True)
  embed1.add_field(name = 'covid vaccine(region, date)', value = 'Gives covid vaccination progress at a specific time, province/health region in Canada. ',inline = True)
  embed1.add_field(name = 'covid cases(region date)', value = 'Gives covid cases, death at a specific time, province/health region in Canada. ',inline = True)

  await ctx.send(embed = embed1)

@client.command(name = 'advice')
async def update(ctx,region):
  try: 
    region1 = dictRegion[region.lower()]
  except:
    listStatus = 'nothing'
  else:
    r = requests.get(f'https://api.opencovid.ca/summary?loc={region1}&date={dateCurrent}')
    json = r.json()
    province = json['summary'][0]['province']
    region = json['summary'][0]['health_region']
    caseNum = json['summary'][0]['cases']
    listStatus = riseCaseStatus(province,dateCurrent,region)
    await ctx.send(embed = getStatusEmbeded(listStatus,caseNum))




def riseCaseStatus(province,date,region):
    listStatus = []
    for a in mapHr[dictP[province]]:
        k = requests.get(f'https://api.opencovid.ca/summary?loc=hr&date={dayBack(date)}')
        json1 = k.json()
        try:
            b = (json1['summary'][a[1]]['cases'] - json1['summary'][a[1]]['cases'])/json1['summary'][a[1]]['cases']
        except:
            b = 0
        if b >= 0.1:
            t = (a[0], True)
        else:
            t = (a[0], False)
        if t[0] == region:
          listStatus.insert(0,t)
        else:
          listStatus.append(t)
    return listStatus

    
def getStatusEmbeded(listStatus,caseNum):
  if listStatus == 'nothing':
    return discord.Embed(title = 'Error', description = 'Please enter a correct location', color = 0x318ca8)
  else:
    message = "Please avoid following areas: "
    for a in range(1,len(listStatus)):
      if listStatus[a][1]:
        message = message + listStatus[a][0] + ' region, '
    if listStatus[0][1]:
      message += 'your own region is not safe too. '
    if message == "Please avoid following areas: ":
      message = 'Your area is currently rather safe from Covid-19 due to majority of people staying at home, but '
    message += 'no matter what, try to stay at home.'
    embed =  discord.Embed(title = 'Advice',description = listStatus[0][0]+' ' + str(caseNum) + ' new cases last 24 hours', color = 0x318ca8)
    embed.add_field(name='Advice',value=message)
    embed.set_footer(text = "Stay at home and stay safe. Please follow the government advice if conflict exists")
    return embed


@client.command()
async def update(ctx):
  update = requests.get(f"https://api.opencovid.ca/version")
  update = update.json()
  update = update["version"]
  worldUpdate = requests.get(f"https://covidapi.info/api/v1/latest-date")
  await ctx.send("Canadian data last updated: {}\nWorld data last updated: {}".format(update,worldUpdate.text))

@client.command()
async def summary(ctx):
  summary = requests.get(f"https://api.covid19api.com/summary")
  summary = summary.json()
  newCases = summary["Global"]["NewConfirmed"]
  totalCases = summary["Global"]["TotalConfirmed"]
  newDeaths = summary["Global"]["NewDeaths"]
  totalDeaths = summary["Global"]["TotalDeaths"]
  newRecoveries = summary["Global"]["NewRecovered"]
  totalRecoveries = summary["Global"]["TotalRecovered"]
  theDate = summary["Global"]["Date"]
  theDate = theDate[:10]
  embed = discord.Embed(title = 'World Summary', description = "Date: {}".format(theDate), color = 0x318ca8)
  embed.add_field(name="New Cases",value=newCases)
  embed.add_field(name="Total Cases", value=totalCases)
  embed.add_field(name="New Deaths",value=newDeaths)
  embed.add_field(name="Total Deaths", value=totalDeaths)
  embed.add_field(name="New Recoveries", value=newRecoveries)
  embed.add_field(name="Total Recoveries", value=totalCases)
  await ctx.send(embed=embed)
   
@client.command()
async def country(ctx, arg, ledate):
  r = requests.get(f"https://covidapi.info/api/v1/country/{dictCountry[arg]}/{ledate}")
  thing = r.json()
  totalCases = thing["result"][ledate]["confirmed"]
  totalDeaths = thing["result"][ledate]["deaths"]
  totalRecovered = thing["result"][ledate]["recovered"]
  if totalRecovered == 0:
    totalRecovered = "No Data"
  embed = discord.Embed(title = arg, description = "Date: {}".format(ledate), color = 0x318ca8)
  embed.add_field(name="Total Cases",value=totalCases)
  embed.add_field(name="Total Deaths", value=totalDeaths)
  embed.add_field(name="Total Recovered",value=totalRecovered)
  await ctx.send(embed=embed) 

def testDate(stringDate):
  if not isinstance(stringDate,str):
    return False
  stringDate = stringDate.split("-")
  if len(stringDate) != 3:
    return False
  try:
    date1 = date(int(stringDate[0]),int(stringDate[1]),int(stringDate[2]))
  except:
    return False
  else:
    if int(stringDate[0])<2020 or int(stringDate[0])>date.today().year:
        return False
    if int(stringDate[0]) == date.today().year:
        if int(stringDate[1])>date.today().month:
            return False
        if int(stringDate[1]) == date.today().month:
            if int(stringDate[2])>date.today().day:
                return False
    return True


@client.command(name = "general")
async def cases(ctx, region='canada', timing='-1'):
  try:
    region = dictProvince[region.lower()]
  except:
    try:
      region = dictRegion[region.lower()]
    except:
      if testDate(region):
        timing = region
  
  if timing == '-1':
    timing = dateCurrent
    # else return error 
  
  await ctx.send(embed = getCOVIDEmbed(region,timing,'General Status'))

@client.command(name = "cases")
async def cases(ctx, region='canada', timing='-1'):
  try:
    region = dictProvince[region.lower()]
  except:
    try:
      region = dictRegion[region.lower()]
    except:
      if testDate(region):
        timing = region

  
  if timing == '-1':
    timing = dateCurrent
    # else return error 
  
  await ctx.send(embed = getCOVIDEmbed(region,timing,'Cases and Death'))

@client.command(name = "vaccine")
async def cases(ctx, region='canada', timing='-1'):
  try:
    region = dictProvince[region.lower()]
  except:
    try:
      region = dictRegion[region.lower()]
    except:
      if testDate(region):
        timing = region

  
  if timing == '-1':
    timing = dateCurrent
    # else return error 
  
  await ctx.send(embed = getCOVIDEmbed(region,timing,'Vaccination Efforts'))
  
def getNumCase(region,timing): 
  try:
    r = requests.get(f"https://api.opencovid.ca/summary?loc={region}&date={timing}")
  except:
    json = 'nothing'
  else:
    json1 = r.json()
    if 'health_region' in json1['summary'][0]:
      a = json1['summary'][0]['health_region']
    else:
      a = -1 
    json=[json1["summary"][0]['province'],
    json1["summary"][0]['date'],
    int(json1["summary"][0]['cumulative_cases']), 
    int(json1["summary"][0]['cases']),
    int(json1['summary'][0]['deaths']),
    int(json1['summary'][0]['cumulative_deaths'])]
    try:
      json.append(int(json1["summary"][0]['cvaccine']))
      json.append(int(json1["summary"][0]['cumulative_cvaccine']))
      json.append(int(json1["summary"][0]['dvaccine']))
      json.append(int(json1['summary'][0]['cumulative_dvaccine']))
      json.append(int(json1['summary'][0]['cumulative_avaccine']))
      json.append(int(json1['summary'][0]['avaccine']))
    except:
      for b in range(6):
        json.append('No Data')
    json.append(a)
    
    #0 province 1 date 2 c.cases 3 new cases 4 new death 5 c.death 6 new cvac 7 c.cvac 8 dvac 9 c.dvac dvac 10 c.avac 11 avac 
  return json

def getCOVIDEmbed(region,timing,type):
  json = getNumCase(region,timing)
  if json == 'nothing':
    return discord.Embed(title = 'Error', description = 'Please enter a correct time/location', color = 0x318ca8)
  if json[-1] != -1:
    embed = discord.Embed(title=type,description="Province: {}, Region: {}, Date: {}".format(json[0],json[-1],json[1]),color=0x318ca8)
  else:
    embed = discord.Embed(title=type,description="Region: {}, Date: {}".format(json[0],json[1]),color=0x318ca8)
  embed.set_thumbnail(url='https://images.unsplash.com/photo-1583324113626-70df0f4deaab?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1189&q=80')
  embed.set_footer(text='Date: {}'.format(datetime.today()))

  if  type != 'Vaccination Efforts':
    embed.add_field(name = "New Cases", value = int(json[3]))
    embed.add_field(name = "Total Cases", value =int(json[2]))
    embed.add_field(name = "New Deaths", value = int(json[4]))
    embed.add_field(name = "Total deaths", value = int(json[5]))
  
  if type != 'Cases and Death':
    embed.add_field(name = "Vaccines administered", value = (json[10]))
    embed.add_field(name = "Total vaccines administered", value =(json[11]))
    embed.add_field(name = "People fully vaccinated", value =(json[6]))
    embed.add_field(name ="Total people fully vacinated", value =(json[7]))
    embed.add_field(name = "Vaccines distributed", value = (json[8]))
    embed.add_field(name = "Total vaccines distributed", value = (json[9]))

  return embed

client.run(os.environ["token"])