#!/usr/bin/env python
# coding: utf-8


# <h1>Исследование рынка заведений общественного питания Москвы</h1>
# Выполнено для фонда «Shut Up and Take My Money»

# [Открытие и первичное изучение данных](#start)<BR>
#     * [Описание данных](#desc)<BR>
# [Предобработка данных](#preprocessing)<BR>
#     * [Проверка на дубликаты](#dupl)<BR>
#     * [Проверка на пропуски](#null)<BR>
#     * [Создание новых столбцов](#mark)<br>
# [Анализ данных](#analysis)<br>
#     * [Распределение по категориям](#category)<br>
#     * [Визуализируем средние рейтинги по категориям](#med_ratings)<br>
#     * [Круглосуточные заведения](#7/24)<br>
#     * [Сетевые заведения](#chain)<br>
#     * [Топ популярных сетей](#topchain)<br>
#     * [Проанализируем посадочные места](#seats)<br>
#     * [Распределение и рейтинги заведений по районам](#dictrict)<br>
#     * [Карта с заведениями](#folium)<br>
#     * [Топ 15 улиц по количеству заведений](#topstreet)<br>
#     * [Улицы с одним заведением](#onepoint)<br>
#     * [Цены по округам и дистанции](#price)<br>
# [Кофейни](#coffee)<br>
#     * [Сколько кофеен в датасете и где они располагаются](#coffee1)
#     * [Кофейни по районам](#coffee2)
#     * [Круглосуточность кофеен](#coffee3)
#     * [Рейтинги](#coffee4)
#     * [Плохие кофейни](#coffee6)
#     * [Стоимость кофе](#coffee5)
#     * [Новый столбец: размер зала кофейни, категоризация](#size)<br>
#     * [Рекомендации](#rec)
#     * [Презентация](#pres)
#     
# <a href='topstreet'></a>     

# Задача:
# - общее исследование рынка заведений общественного питани Москвы
# - Основателям фонда «Shut Up and Take My Money» не даёт покоя успех сериала «Друзья». Их мечта — открыть такую же крутую и доступную, как «Central Perk», кофейню в Москве. Будем считать, что заказчики не боятся конкуренции в этой сфере, ведь кофеен в больших городах уже достаточно. Попробуйте определить, осуществима ли мечта клиентов.

# <a href='start'></a>
# <h2>Открытие данных</h2>

# In[ ]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


data=pd.read_csv('/datasets/moscow_places.csv')
display(data.head())


# In[ ]:


print(data.info())


# <a href='desc'></a>
# Таблица содержит 8406 записей о московских заведениях общественного питания. Для каждой записи указана категория заведения (строка), адрес (строка), район расположения (строка), широта и долгота географической точки расположения (число с плавающей точкой), рейтинг (число с плаваюшей точкой), признак принадлежности к сети в формате 0 или 1 (целое число).<br>
# Для 7870 записей указаны часы работы (строка).<br>
# Для 3315 записей указана ценовая категория заведения (строка) - рабочие дни, рабочие часы
# Для 3816 записей указана средняя стоимость заказа, из них для 3149 записей указан средний счет, а для 535 – стоимость чашки капучино (число с плавающей точкой).<br>
# Для 4795 указано количество посадочны мест (число с плавающей точкой)


# <a href='preprocessing'></a>
# <h1>Предобработка данных</h1>

# <a href='dupl'></a>
# <h1>Проверка на дубликаты</h1>

# In[ ]:


#Проверим датасет на явные дубликаты
data.duplicated().sum()


# Полные дубликаты записей отсутствуют

# Возможно, есть неполные дубликаты? Проверим это.


# In[ ]:


duplicateRows = data[data.duplicated(['name', 'address'])]

print(len(duplicateRows))


# На первый взгляд, очевидных совпадений по адресу и названию нет

# In[ ]:


print('Уникальных названий заведений ',len(data['name'].unique()))


# In[ ]:


data['name'] = data['name'].str.lower()
data['address'] = data['address'].str.lower()
#приведем названия и адреса к одному регистру


# In[ ]:


#еще раз проверим датасет на явные дубликаты
data.duplicated().sum()


# In[ ]:



duplicateRows = data[data.duplicated(['name', 'address'])]

print(len(duplicateRows))


# In[ ]:


duplicateRows


# Нашлось четыре дублирующихся записи

# In[ ]:


#удалим повторы, оставив только первую запись, перезапишем таблицу
data=data.drop_duplicates(['name', 'address'])


#проверим
duplicateRows=data[data.duplicated(['name', 'address'])]

duplicateRows


# проверены совпадения по двум столбцам, таблица перезаписана, дубликаты отсутствуют

# In[ ]:


print('Уникальных названий заведений ',len(data['name'].unique()))


# In[ ]:


d_name = data[data.duplicated(['name'])]
d_name.groupby('name')['address'].count().sort_values(ascending=False).head(20)


# Дубликаты в этом столбце связаны с приинадлежностью к сети либо с отсутствием названия у заведения (см. Кафе, ресторан). Не будем считать их дубликатами, так как у них различаются адреса.

# In[ ]:


#таким же образом проанализируем срез "дубликатов" по адресам
d_address = data[data.duplicated(['address'])]
test_group=d_address.groupby('address')['name'].count().sort_values(ascending=False).head(20)
test_group=pd.DataFrame({'address':test_group.index, 'points':test_group.values})


# Москва, проспект Вернадского, 86В - самый большой фудхолл на юго-западе, Москва, Усачёва улица, 26 - Усачевский рынок, Москва, Ярцевская улица, 19  - Кунцево Плаза, то есть все это – типичные места группировки небольших заведений общественного питания, часто сетевых. Проверим эту теорию.       

# In[ ]:


test_data = test_group.merge(data, left_on = 'address', right_on='address', how='left')
test_data.groupby('chain')['name'].count()


# Полагаю, с датасетом все в порядке: данные ведут себя в целом достаточно предсказуемо, ошибочных записей, которые могли бы портить статистику, нет или очень мало.

# In[ ]:


print('Заведения распределены по следующим категориям:',data['category'].unique())


# In[ ]:


print('Описаны заведения из следующих ценовых категорий:',data['price'].unique())


# In[ ]:


print('Округа присутствия:',data['district'].unique())


# Посмотрим на пропуски 

# In[ ]:


nans=data.isna()
sns.set(rc = {'figure.figsize':(16,6)})
sns.heatmap(nans.transpose(), cbar=False).set_title('Соответствия данных по местам пропусков');


# Пропуски имеются в столбцах:  hours, price, avg_bill, middle_avg_bill, middle_coffee_cup и seats, все связаны с ценой  либо возможным количеством клиентов.
# Количество посадочных мест в заведении общественного питания восстановить не представляется возможным, однако проверить, имеется ли общая ценовая политика в сетевых заведения, можно.
# Разделим все записи на записи о сетевых и несетевых заведениях


# In[ ]:


print('Уникальные значения в столбце  chain:',data['chain'].unique())
chain_item =data.query('chain==1')
no_chain_item = data.query('chain==0')
print('Сетевых заведений в датасете:',len(chain_item))
print('Несетевых заведений:',len(no_chain_item))


# In[ ]:


chain_item.isna().sum() #уточним, много ли пропусков в сетевых заведениях


# In[ ]:


chain_grouping = chain_item.groupby('name')['address'].count()
print(chain_grouping.sort_values(ascending=False))


# In[ ]:


shoko=data.query('name=="шоколадница"')
display(shoko['avg_bill'].unique())


# Формат записей о ценах в заведениях крупной сети различен, сами данные также имеют большой разброс, то есть сделать вывод об общей ценовой политике нельзя (так же, как и заполнить пропуски имеющимися значениями.
# Предполагаю, что данные вносились вручную - отсюда опечатки типа 'Цена чашки капучино:230–2907 ₽'


# In[ ]:


dodo=data.query('name=="додо пицца"')
display(dodo['avg_bill'].unique())


# Оставим пропуски как есть

# <a href='mark'></a>
# <h1>Создание новых столбцов</h1>

# In[ ]:


#достанем улицу из адреса 
street=[]
for value in data['address']:
    value=value.rsplit(',')
    #print(value[1])
    street.append(value[1])

#и добавим новым столбцом в таблицу
data['street']=street
display(data.head())
#кажется, все ок


# In[ ]:


data['hours'] = data['hours'].astype( str )

#приведем значения в столбце к типу строка


# <a href='7/24'></a>
# Создадим разметочный столбец для времени работы: разделим все заведения на открытые круглосуточно и без выходных, и нет

# In[ ]:



status = []
for value in data['hours']:
    if 'ежеднев' in value and 'круглосут' in value:
        status.append(True)
    else:
        status.append(False)
    
data['is_24/7']=status


# In[ ]:


open24_points=data.groupby('is_24/7')['name'].count()
labels = ['Не круглосуточные', 'круглосуточные']
colors = sns.color_palette('pastel')[ 0:2 ]
print('Соотношение круглосуточных и некруглосуточных заведений')
plt.pie(open24_points, labels = labels, colors = colors, autopct='%.0f%%', )
plt.show(); #прикинем долю круглосуточных заведений в Москве


# <a href='analysis'></a>
# <h1>Анализ данных</h1>

# <a href='category'></a>
# <h2>Распределение заведений по категориям</h2>

# In[ ]:


parts=data.groupby('category')['name'].count().sort_values().plot(kind='barh', title='Распределение заведений по категориям', xlabel='Типы заведений')

#plt.ylabel='Тип заведения'


# In[ ]:


data.groupby('category')['name'].count().sort_values(ascending=False)


# В Москве больше всего кафе, вторую по значению долю с небольшим отрывом представляют рестораны, следующая по количеству категория - кофейни, за ними с большим отрывом (вдвое меньше) следуют другие специализированные заведения – бары и пабы, пиццерии, фастфуд заведения. Меньше всего булочных.

# <div class="alert alert-success">
# <h2> Комментарий от ревьюера<a class="tocSkip"></a></h2>
# Да, абсолютно верно👌 Кафе в этом датафрейме больше всего
#     
#  
# </div>

# In[ ]:


data['seats'].describe()


# Среднее количество посадочных мест – 108, максимальное – 1288, минимальное - 0 (еда навынос?)


# In[ ]:


no_seats = data.query('seats == 0')
no_seats.groupby('address')['name'].count().sort_values(ascending=False)


# Поречная 10 - торгово-развлекательный центр, Мячковский бульвар, 3А - Братиславский рынок,Москва, Семёновская площадь, 7, корп. 17А - тоже торговый центр
# 
# Похоже на правду: здесь может быть много мелких торговых точек с едой навынос и без зала
# 

# <a href='seats'></a>    
# Посмотрим, как обстоят дела с <b>посадочными местами</b>

# In[ ]:


data['seats'].isna().sum()


# Очень много невосстанавливаемых пропусков

# In[ ]:


data.pivot_table(index='category', values='seats', aggfunc=['median','min','max','mean']).plot(grid=True, style='o-', figsize=(10, 10),title='Количество посадочных мест', ylabel='Количество мест',xlabel='Типы заведений');


# Интересный факт: самые большие булочные не бывают такими же большими, как другие заведения, а большие фастфуды меньше больших кафе, ресторанов, пиццерий и кофеен

# In[ ]:


data.pivot_table(index='category', values='seats', aggfunc='median').sort_values(by='seats').plot(kind='barh', legend=False, title='Медианное количество посадочных мест по категориям',xlabel='Типы зведений');


# В целом рестораны крупнее, чем бары и и кофейни, а пиццерии, булочные и кафе – это скорее небольшие заведения.Столовые и предприятия быстрого питания – нечто среднее по размерам.

# <a href='chain'></a>
# Найдем долю сетевых и несетевых заведений

# In[ ]:


chain_item =data.query('chain==1')
no_chain_item = data.query('chain==0')
chains_part=data.groupby('chain')['name'].count()
labels = ['Не сетевые', 'Сетевые']
colors = sns.color_palette('pastel')[ 0:2 ]
print('Соотношение сетевых и несетевых заведений')
plt.pie(chains_part, labels = labels, colors = colors, autopct='%.0f%%', )
plt.show(); #прикинем долю сетевых заведений в Москве


# Сетевых заведений меньше, чем отдельных


# In[ ]:


table_one=chain_item.groupby('category')['name'].count()
table_two=no_chain_item.groupby('category')['name'].count()
count_chain = {"Сетевые": table_one,
        "Несетевые": table_two}
df = pd.concat(count_chain, axis = 1)
df.plot(kind='barh');


# Сетевыми чаще бывают кофейни, булочные и пиццериии, в остальных категориях очевидно превалируют отдельные заведения. Особенно хорошо заметен перевес отдельных заведений в категориях Кафе, Бар/паб, Ресторан и Столовая

# In[ ]:



df['chain_part'] = round(df['Сетевые']/(df['Сетевые']+df['Несетевые'])*100)
print(df)


# Кажется очевидным, что для булочных (61 процент сетевых заведений), пиццерий (52) и кофеен (51) характерно сетевое распространение



# <a href='topchain'></a>    
# <h2>Топ популярных сетей</h2>

# In[ ]:


data.groupby('name')['address'].count().sort_values(ascending=False).head(15)


# В списке встречаются такие название, как "кафе", "ресторан" и "шаурма". Очевидно, что это просто малые, возможно. частные заведения, не имеющие самоназвания – просто кафе, расположенное по адресу.
# Кажется, что при оценке популярности сетей стоит рассматривать только те заведения, которые имеют признак "сетевое". Проделаем то же самое упражнения для среза сетевых заведений.


# In[ ]:


chain_item.groupby('name')['address'].count().sort_values(ascending=False).head(15).plot(kind='barh',title='Топ15 популярных сетей в Москве', xlabel='Название сетей');


# Список изменился – теперь это больше похоже на топ15 популярных по Москве сетей


# In[ ]:


ch_i = chain_item.groupby(['name','category'], as_index=False)['address'].count().sort_values(by='address', ascending=False).head(15)
display(ch_i)


# В топ15 сетевых заведений Москвы вошло 6 кофеен – и это больше, чем любых других заведений общественного питания

# <a href='district'></a>    
# <h2>Заведения по районам и их рейтинги</h2>

# In[ ]:


data.groupby('district')['address'].count().sort_values(ascending=False).head(15).plot(kind='barh');


# В Центральном округе предсказуемо больше заведений, чем в любом другом. Посмотрим, как они распределены

# Центральный район любого города, иногда называемый старым городом – туристическое место (+ к проходимости). Вместе с этим здесь обычно находятся центры деловой активности и дорогие офисы (+к проходимости за счет назначения встреч и бизнес-ланчей), а также это часто удобная точка встречи, равноудаленная от окраин (+к проходимости). Полагаю, что проходимость – главный бизнес-показатель для заведений общественного питания.

# In[ ]:


def heatmap(data, index, columns, values, aggfunc, title):
    data = data.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)
    sns.heatmap(data,annot=True,cmap='Blues', fmt='g')
        
heatmap(data, 'district', 'category', 'address', 'count', 'Распределение категорий по районам')


# Большая часть ресторанов сосредоточена в Центральном округе, то же, хотя и в меньше степени, относится к кафе, кофейням и барам.
# Не выявлено заметного разброса по сосредоточению булочных, столовых и точек фастфуда.
# Наименьшее количество кафе, ресторанов, булочных, баров и пиццерий – в Северо-Западном округе, наименьшее количество столовых - в Юго-Западном (за ним следуют Западный и Юго-Восточный округа)
# 

# <a href='med_ratings'></a>
# Найдем средние рейтинги по категориям заведений

# In[ ]:


category_mean_rating = data.groupby('category').agg({'rating': 'mean'}).round(2).sort_values('rating', ascending=False).reset_index()
category_mean_rating


# In[ ]:


data.groupby('category')['rating'].mean().sort_values(ascending=True).plot(kind='barh', title='Распределение средних рейтингов по категориям', xlabel='Категории');


# In[ ]:


#на всякий случай сравним с медианными значениями – вдруг есть какой-то выброс, который портит картинку
data.groupby('category')['rating'].median().sort_values(ascending=True).plot(kind='barh', title='Распределение медианных рейтингов пр категориям',xlabel='Категории');


# Медианные и средние рейтинги по категориям различаются довольно слабо: все выше 4 и ниже 5.
# Бары/пабы получают более высокие средние и медианные оценки. У пиццений сравнительно высокий средний рейтинг (2 место), но более низкий медианный (4 место). Предположу, что есть сравнительно небольшая часть пиццерий со сверхвысокими рейтингами, которые и дают такой разброс между средним и медианным, более устойчивым к выбросам значениями.
# Столовые, напротив, имеют низкий средний (6 место), но высокий медианный рейтинг (2 место).


# <a href='chor'></a>
# 
# Построим хороплет со средним рейтингом для каждого района
# 
# 

# In[ ]:


rating_data = data.groupby(['district','category'], as_index=False)['rating'].mean().sort_values(by='rating', ascending=False).round(2)
rating_data


# In[ ]:


rating_median = data.groupby(['district','category'], as_index=False)['rating'].median().sort_values(by='rating', ascending=False).round(2)


# In[ ]:


def heatmap2(data, index, columns, values, aggfunc, title):
    data = data.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)
    plt.figure(figsize=(14,6))
    plt.title(title)
    sns.heatmap(data, annot=True)
    plt.show()
    
heatmap2(data, 'district', 'category', 'rating', 'mean', 'Средний рейтинг категорий по районам')


# Кажется, что самые низкие средние рейтинги у заведений в категории "быстрое питание", особенно печальная картина - в Северо-Западном и Юго-восточным округам (дальние окраины?). В категории "кофейни" рейтинг чрезвычайно ровный, по округам различается очень мало.


# In[ ]:


from folium import Map, Choropleth
# загружаем JSON-файл с границами округов Москвы
state_geo = 'https://code.s3.yandex.net/data-analyst/admin_level_geomap.geojson'
# moscow_lat - широта центра Москвы, moscow_lng - долгота центра Москвы
moscow_lat, moscow_lng = 55.751244, 37.618423

# Рисуем карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

# собираем хороплет с помощью конструктора Choropleth и добавляем его на карту
Choropleth(
    geo_data=state_geo,
    data=rating_data,
    columns=['district', 'rating'],
    key_on='feature.name',
    #fill_color='YlGn',
    #fill_opacity=0.8,
    legend_name='Средний рейтинг заведений по районам',
).add_to(m)

# вывод карты
m


# Видим, что:<br>
# - заведения в центре Москвы оцениваются в среднем выше
# - у Северо-западного, западного и юго-западного округов оценки ниже, то же касается юго-восточного


# In[ ]:


#проверим по медианным значениям - нет ли разницы?
moscow_lat, moscow_lng = 55.751244, 37.618423

# Рисуем еще одну карту Москвы
p = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

Choropleth(
    geo_data=state_geo,
    data=rating_median,
    columns=['district', 'rating'],
    key_on='feature.name',
    #fill_color='YlGn',
    #fill_opacity=0.8,
    legend_name='Медианный рейтинг заведений по районам',
).add_to(p)

# вывод карты
p


# Здесь проблема с качеством заведений по рейтингам прокрашена гораздо отчетливее.

# <a href='folium'></a>    
# <h2>Карта с заведениями</h2>
# •	Отобразите все заведения датасета на карте с помощью кластеров средствами библиотеки folium.

# In[ ]:


# импортируем карту и хороплет
from folium import Marker
from folium.plugins import MarkerCluster
from folium.features import CustomIcon

# moscow_lat - широта центра Москвы, moscow_lng - долгота центра Москвы
moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
all_items = Map(location=[moscow_lat, moscow_lng], zoom_start=10)
# создаём пустой кластер, добавляем его на карту
marker_cluster = MarkerCluster().add_to(all_items)

def create_clusters(row):
    # сохраняем URL-адрес изображения,
    # это путь к файлу на сервере icons8
    icon_url = 'https://img.icons8.com/?size=512&id=kWhYV4LAfd3x&format=png'  
    # создаём объект с собственной иконкой размером 30x30
    icon = CustomIcon(icon_url, icon_size=(30, 30))
    
    # создаём маркер с иконкой icon и добавляем его в кластер
    Marker(
        [row['lat'], row['lng']],
        popup=f"{row['name']}",
        icon=icon,
    ).add_to(marker_cluster)

# применяем функцию для создания кластеров к каждой строке датафрейма
data.apply(create_clusters, axis=1)

# выводим карту
all_items


#  Заведения общественного питания заметно тяготеют к центральному округу, меньше всего их на юго-востоке и в восточных районах

# <a href='topstreet'></a>    
# <h2>Топ15 улиц по количеству заведений</h2>

# In[ ]:


#Найдем топ15 улиц по количеству заведений
t_street=data.groupby('street')['name'].count().sort_values(ascending=False).head(15)
#сделаем из него таблицу
street=pd.DataFrame({'street':t_street.index, 'points':t_street.values})


# In[ ]:


#заберем все, что есть по этим улицам, из основного датафрейма
top_data = street.merge(data, left_on = 'street', right_on='street', how='left')

print('Объектов, расположенных на улицах из топ15', len(top_data))


# In[ ]:


#посчитаем распределение по категориям
top_data.groupby(['category'])['name'].count().sort_values(ascending=False).head()


# Больше всего кафе, за ними следуют рестораны; выведем график и посмотрим, какие улицы вложились в эти цифры

# In[ ]:


plt.figure(figsize=(10, 20))
c=sns.countplot(y='street', hue='category', data=top_data)
c.set_xlabel('Количество заведений')
c.set_ylabel('Улицы')

plt.xticks(rotation=45)
plt.title('Распределение категорий по улицам')
plt.legend(loc='lower right')
plt.show()


# Лидеры по количеству кафе – Проспект мира, Профсоюзная, МКАД, Люблинская и Миклухо-Маклая
# все это - не центральные улицы
# 
# Рестораны заметно представлены на Пятницкой, Кутузовском проспекте, Ленинском проспекте, Ленинградском шоссе и Ленинградском проспекте, Дмитровском шоссе и проспекте Вернадского – это районы с дорогой недвижимость и высокой проходимостью.
# 
# Бары и пабы тяготеют к Проспекту Мира, Пятницкой улице, Ленинскому и Ленинградскому проспектам,


# In[ ]:


#сделаем общий список по улицам с количеством заведений и будем пользоваться им в дальнейшем
streets = (
    data.groupby('street')
    .agg({'name':'count'})
    .reset_index()
    .sort_values(by='name', ascending=False)
    .rename(columns={'name':'points'})
)


# <a href='onepoint'></a>   
# <h2>Улица с одним объектом</h2>

# In[ ]:


#составим список тех улиц, где находится только один объект
one_point = streets.query('points ==1')
#и заберем данные по эти объектам
one_data = one_point.merge(data, left_on = 'street', right_on='street', how='left')


# In[ ]:


#какие это заведения, есть ли у них особености?
one_data.groupby(['category'])['name'].count().sort_values(ascending=False)


# In[ ]:


plt.figure(figsize=(10, 20))
с=sns.countplot(y='category', hue='chain', data=one_data)
plt.title('Распределение категорий по признаку принадлежности к сети')
plt.legend(title='Принадлежность', loc='upper right', labels=['Независимое', 'Сетевое'])
plt.show()


# In[ ]:


plt.figure(figsize=(10, 20))
sns.countplot(y='category', hue='price', data=top_data)
plt.xticks(rotation=45)
plt.title('Распределение категорий по ценовой политике')
plt.legend(loc='lower right')
plt.show()


# Один объект на улице – это средней ценовой категории отдельное заведение, чаще всего – кафе, иногда сетевая пиццерия


# <a href='price'></a>  
# <h2>Цены в заведениях Москвы</h2>

# In[ ]:


price_ind= (
    data.groupby('district')
    .agg({'middle_avg_bill':'median'})
    .reset_index()
    .sort_values(by='middle_avg_bill', ascending=False)
    .rename(columns={'middle_avg_bill':'price'})
)
print('Ценовой индекс по районам')
print(price_ind)


# In[ ]:


moscow_lat, moscow_lng = 55.751244, 37.618423

# Нарисуем еще одну карту Москвы
i = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

Choropleth(
    geo_data=state_geo,
    data=price_ind,
    columns=['district', 'price'],
    key_on='feature.name',
    #fill_color='YlGn',
    #fill_opacity=0.8,
    legend_name='Медианный прайс заведений по районам',
).add_to(i)

# вывод карты
i


# На хороплете видно, что высокий средний чек в Западном и Центральном округах, низкий – в Северо-Восточном, Южном и Юго-Восточном (что в принципе похоже на правду, это недорогие районы с большими промзонами и не слишком платежеспособной аудиторией).
# Кажется, что при удалении от центра цены в заведениях общественного питания падают. Проверим это.

# In[ ]:


pip install geopy 


# In[ ]:


# загружаем нужную библиотеку
from geopy.distance import geodesic as GD 
#обозначаем центр
center = (55.751244, 37.618423) 
#допустим, что направление и район расположения сейчас неважны и будем мерять расстояние от точки центра   
#склеим широту и долготу в координаты
data['full_coord']=data['lat'].astype(str)+', '+data['lng'].astype(str)

#посчитаем расстояние в километрах и округлим до целых километров, заведем для этих данных дополнительный столбец
distance=[]
for each in data['full_coord']:
    each=int(GD(center, each).km)
    distance.append(each) 
data['distance']=distance

#Построим корреляционную матрицу

y = data['distance']
x = data['middle_avg_bill']
correlation = y.corr(x)
print(correlation)

# plotting the data
plt.scatter(x, y,  label = 'Средний чек в заведении на километр')

plt.title('Разброс цен по удаленности от центра Москвы')


plt.legend();
 


# Корреляция между этими величинами, кажется, довольно слабая, но при удалении от центра цены тяготеют к понижению

# In[ ]:


#посмотрим по километрам детально
data.groupby('distance')['middle_avg_bill'].median().plot(kind='barh', title='Изменения среднего чека по расстоянию от центра', ylabel='Средний чек',xlabel='Расстояние в км');

# Однако видно, что в радиусе 3 километров от центра медианные ценовые показатели заметно выше, чем в других местах – это очень примерно зона внутри Садового Кольца. Особенно это касается удаленности в 1 километр (вероятно, золотой треугольник?). На 8 (ТТК), 14 и 19 (МКАД и выезды из города) километрах снова заметен рост.
# Возможно, эти цифры связаны не столько с удаленностью, сколько с проходимостью и наличием рядом интересущих посетителей объектов, например, парка Царицыно и похожих.


# <a href='coffee1'></a>  
# <h1>Шаг 4. Детализируем исследование: открытие кофейни</h1>

# In[ ]:


coffee_data = data[data['category'] == 'кофейня']
print('Кофейни, всего:', len(coffee_data))
# создаем карту
coffee = Map(location=[moscow_lat, moscow_lng], zoom_start=10)
# создаем пустой кластер и добавляем его на карту
marker_cluster = MarkerCluster().add_to(coffee)

# функция, которая принимает строку датафрейма,
# создаёт маркер в текущей точке и добавляет его в кластер marker_cluster

def create_clusters(row):
    Marker(
        [row['lat'], row['lng']],
        popup=f"{row['name']} {row['rating']}",
    ).add_to(marker_cluster)

# применяем функцию create_clusters() к каждой строке датафрейма
coffee_data.apply(create_clusters, axis=1)

# выводим карту
coffee


# <a href='coffee2'></a>  

# In[ ]:



coffee_data.groupby('district')['address'].count().sort_values().plot(kind='barh', title='Количество кофеен по округам',xlabel='Округ');


# Подавляющее большинство кофеен расположено в Центральном административном округе, на втором месте с большим отрывом – Северный административный округ, на третьем – Северо-восточный.


# Кофейни – хорошее место для деловых и личных встреч, во время работы или прогулок люди часто пьют кофе. В Центральном округе довольно много офисов и мест, привлекательных для прогулок – полагаю, что поэтому.

# In[ ]:


#Найдем топ15 улиц по количеству заведений
coffee_street=coffee_data.groupby('street')['name'].count().sort_values(ascending=False).head(15)
coffee_barh = coffee_street.plot(kind='barh',title='Количество кофеен по улицам')


# Самая "кофейная" улица - Проспект Мира.

# In[ ]:


#сделаем из него таблицу
coffee_by_street=pd.DataFrame({'street':coffee_street.index, 'points':coffee_street.values})
#заберем все, что есть по этим улицам, из основного датафрейма
coffee_data_fin = coffee_by_street.merge(data, left_on = 'street', right_on='street', how='left')

print('Кофеен, расположенных на улицах из топ15', len(coffee_data_fin))
print('А на остальных - всего',len(coffee_data)-len(coffee_data_fin))


# <a href='coffee3'></a>  
# <h2>Круглосуточность кофеен</h2>

# In[ ]:


open_24=coffee_data_fin.groupby('is_24/7')['name'].count()
labels = ['Не круглосуточные', 'круглосуточные']
colors = sns.color_palette('pastel')[ 0:2 ]
print('Соотношение круглосуточных и некруглосуточных кофеен')
plt.pie(open_24, labels = labels, colors = colors, autopct='%.0f%%', )
plt.show()


# Круглосуточные кофейни существуют, но их всего 8%

# <a href='coffee4'></a>  
# </h2>Рейтинги кофеен</h2>

# Какие у кофеен рейтинги? Как они распределяются по районам?
# 

# In[ ]:


coffee_data['rating'].describe()


# Средний рейтинг московской кофейни – 4,2, стандартное отклонение низкое,значения тяготеют к средним. Минимальное значение рейтинга 1,4 максимальное - 5.

# In[ ]:


coffee_data.groupby('rating')['name'].count().plot(kind='bar');


# Больше всего кофеен с рейтингом 4.3, на втором месте - 4.4. Заметен длинный "хвост" по настоящему плохих кофеен


# <a href='coffee6'></a>  
# <h2>Плохие кофейни</h2>

# In[ ]:


bad_coffee = coffee_data.query('rating <3.7')


# In[ ]:


len(bad_coffee)


# Их всего 56 по Москве

# In[ ]:


bad_coffee.groupby('district')['name'].count().sort_values().plot(kind='barh');


# Меньше всего плохих кофеен в Северо-Западном округе, больше всего - В Юго-восточном и Северо-восточном округах

# In[ ]:


median_coffee=coffee_data.groupby('district')['rating'].median()


# Медианный рейтинг по районам практически одинаков на исключением Западного округа – тут он ниже

# In[ ]:


mean_coffee=coffee_data.groupby('district')['rating'].mean()
mean_coffee


# Изучение средних рейтингов также указывает на проблемы в Западном округе, однако тут еще видно, что и Северо-Восточный также отстает по рейтингам

# In[ ]:


median_coffee


# In[ ]:


coffee_data.groupby('distance')['rating'].median()


# Рейтинг не связан с удаленностью от центра

# In[ ]:


bad_coffee.groupby('distance')['rating'].median()


# Однако можно ответить, что в радиусе 1 км от центра плохих кофеен нет

# In[ ]:


coffee_data.head()


# <a href='coffee5'></a>  
# <h2>Стоимость кофе</h2>

# In[ ]:


coffee_ind=coffee_data.groupby('district')['middle_coffee_cup'].median()
print(coffee_ind)
coffee_data.groupby('district')['middle_coffee_cup'].median().sort_values().plot(kind='barh', title='Стоимость средней чашки капучино', xlabel='Округ', ylabel='Стоимость, руб.');

# In[ ]:


moscow_lat, moscow_lng = 55.751244, 37.618423

# Нарисуем еще одну карту Москвы
j = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

Choropleth(
    geo_data=state_geo,
    data=coffee_ind,
    columns=['district', 'price'],
    key_on='feature.name',
    #fill_color='YlGn',
    #fill_opacity=0.8,
    legend_name='Медианный прайс кофеен по районам',
).add_to(j)

# вывод карты
j


# Самая высокая средняя стоимость чашки кофе – в Юго-Западном округе, Самая низкая - в Восточном.

# In[ ]:


coffee_data.groupby('distance')['middle_coffee_cup'].median().plot(kind='barh');


# В центре (0 и 1 км) и на 18 километре самый дорогой кофе, самый дешевый, на 13 и 17

# In[ ]:


coffee_data.groupby(['district','distance'], as_index=False)['middle_coffee_cup'].median().sort_values(by='middle_coffee_cup', ascending=False).head(15)


# В случае, если заказчику в первую очередь интересна чистая прибыль заведения, стоит обратить внимание на относительно удаленные и среднеудаленные от центра локации в Северо-Западном и Западном округах

# In[ ]:


street_recommend=coffee_data.query('district =="Западный административный округ"').groupby(['district','street','distance'], as_index=False)['middle_coffee_cup'].median().sort_values(by='middle_coffee_cup', ascending=False).head(15)
street_recommend


# Рекомендуется внимательно изучить подходящие для аренды помещения на Ярцевской улице (13 км от центра), Площади Победы (6 км от центра), улице 1812 года (6 км от центра), Кутузовском проспекте (5 км от центра) и Осенней улице (13 км от центра). Вероятно, есть причины, которые обуславливают высокую стоимость чашки кофе в этих локациях.


# In[ ]:


coffee_data.groupby(['district','distance'], as_index=False)['rating'].median().sort_values(by='rating', ascending=False).head(15)


# In[ ]:


coffee_data.groupby(['street','distance'], as_index=False)['rating'].median().sort_values(by='rating', ascending=False).head(15)


# In[ ]:


rating_recommend=coffee_data.query('district =="Северо-Западный административный округ"').groupby(['district','street','distance'], as_index=False)['rating'].median().sort_values(by='rating', ascending=False).head(15)
rating_recommend


# Если инвестор ориентируется на узнаваемость и желание заслужить высокую оценку, стоит обратить внимание на Северо-Западный округ. Рекомендуется внимательно изучить подходящие для аренды помещения в 3 Силикатном проезде(7 км), Светлогорском проезде(17 км), на улице Свободы(13 км), Карамышевской набережной (9 км) и Туристской улице (16 км).

# In[ ]:


#Построим корреляционную матрицу

y = coffee_data['rating']
x = coffee_data['middle_coffee_cup']
correlation = y.corr(x)
print(correlation)

# plotting the data
plt.scatter(x, y,  label = 'Зависимость рейтинга от средней цены чашки кофе')

plt.legend();


# Крайне слабая положительная корреляция: с ростом цены едва заметно повышается вероятность получить хороший рейтинг


# Рекомендуемая цена чашки капучино в новом заведении – 250-300 рублей

# In[ ]:


#посчитаем соотношение сетевых и несетевых заведений в группе кофеен
coffee_chain=coffee_data.groupby('chain')['name'].count()
labels = ['Не сетевые', 'Сетевые']
colors = sns.color_palette('pastel')[ 0:2 ]
print('Соотношение сетевых и несетевых кофеен')
plt.pie(coffee_chain, labels = labels, colors = colors, autopct='%.0f%%', )
plt.show()


# In[ ]:


#посмотрим на корреляцию рейтингов и признака принадлежности к сети
y = coffee_data['rating']
x = coffee_data['chain']
correlation = y.corr(x)
print(correlation)


# In[ ]:


#посчитаем медианное значение рейтинга по группам
coffee_data.groupby('chain')['rating'].median()


# У несетевых кафе медианное значение рейтинга на две десятых пункта выше, чем у сетевых: вероятно, они больше нравятся людям благодаря своей индивидуальности

# In[ ]:


coffee_data['seats'].describe()


# <a href='size'></a>
# <h1>Размер зала: дополнительный столбец</h1>

# In[ ]:


#разметим кофейни по размеру зала
cd=coffee_data.copy()
size =[]
for value in cd['seats']:
    if value == 0:
        size.append('навынос')
    elif 0<value<=12:
        size.append('крошечное')
    elif 12<value<=40:
        size.append('маленькое')
    elif 40<value<=80:
        size.append('среднее')
    else:
        size.append('большое')
cd['size'] = size


# In[ ]:


#сгруппируем по полученным группам, чтобы посмотреть, есть ли разница в рейтингах
cd.groupby('size')['rating'].median().sort_values().plot(kind='barh');


# У крошечных и маленьких (от 1 до 40 сидячих мест включительно) больше шансов заслужить рейтинг чуточку выше, чем у больших кофеен.


# <a href='rec'></a>
# <H1>Рекомендация</H1>
# Рекомендация: открыть небольшое (до 40 мест) несетевое кафе, со стоимостью 250-300 рублей за чашку капучино. Наиболее интересными локациями выглядит Северо-Западный округ и Западный округа. Рекомендуется внимательно изучить подходящие для аренды помещения в 3 Силикатном проезде(7 км), Светлогорском проезде(17 км), на улице Свободы(13 км), Карамышевской набережной (9 км) и Туристской улице (16 км) – там располагаются в целом высокорейтинговые заведения, а также на Ярцевской улице (13 км от центра), Площади Победы (6 км от центра), улице 1812 года (6 км от центра), Кутузовском проспекте (5 км от центра) и Осенней улице (13 км от центра). Вероятно, есть причины, которые обуславливают высокую стоимость чашки кофе в этих локациях.
# Если это возможно, стоит открыть кофейню, работающую круглосуточно – это выгодно выделит заведение из массы прочих
# 

# <a href='prez'></a>  
# <a href=https://disk.yandex.ru/i/Dq63uzbEqEkZZg>Общая презентация</a>
# 

# In[ ]:




