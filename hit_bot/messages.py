# -*- coding: utf-8 -*-

START_MESSAGE = {'de': '*SWR1 Hitparade 2019*\n\n\
Ich bins, der Hitparaden Bot.\n\
Wenn Du wissen möchtest, welcher Titel wo in der Hitparade 2019 gelandet ist, dann frag einfach mich.\
Gib dafür einfach einen Suchbegriff ein und los geht\'s. Wenn Du wissen willst wie es genau funktioniert, sende einfach / hilfe an mich.\n\n\
*ACHTUNG*\nDieser Bot ist ein rein privates Projekt und hat nichts mit dem Radiosender SWR1 zu tun!'}

HELP_MESSAGE = {'de': '*Hitparaden Bot-Hilfe*\n\n\
Sende einfach einen beliebigen Text an mich und ich suche in der gesamten Liste der gewählten Titel nach diesem Text.\
Du kannst die Suche aber auch auf bestimmte Felder einschränken.\n\n\
*/platz* - Sucht nach der der gewünschten Platzierung.\n\
*/titel* - Sucht nur im Titel.\n\
*/musiker* - Sucht nur innerhalb der Künstler.\n\
*/anzahl* - Zählt die Anzahl der Titel des gesuchten Musikers.\n\
*/10* - Gibt die Top Ten aus\n\n\
*/hilfe2* - Dort kannst Du schauen, wie Du Deine Sucht noch verfeinern kannst'}

HELP_MESSAGE2 = {'de': '*Erweiterter Syntax für die Suche*\n\n\
Im Normalfall wird einfach nach allen angegebenen Suchbegriffen gesucht und alle Ergebnisse, in denen einer der Suchbegriffe vorkommt, werden angezeigt.\
Die Suchbegriffe sind also mit ODER verknüpft.\
Mit folgende Erweiterungen kannst Du Deine Suche etwas verfeinern: \n\
+ - Mit einem Plus vor dem Suchbegriff wird dieser mit UND verknüpft.\n\
"" - Schließt du mehrere Suchbegriffe mit Hochkommata ein wird genau nach dieser Zeichenfolge gesucht.'}

NO_EMPTY_SEARCH = {'de': 'Autsch, da hast Du wohl was vergessen. Die Suche darf *nicht* leer sein.'}

NO_HIT_COUNT = {'de': '*Schade*\nDer Künstler hatte keinen Hit in der Hitparade. Probier es doch gleich noch einmal.'}

NO_NUM = {'de': 'Um nach einer Platzierung zu suchen musst Du eine Zahl eingeben.'}


def hit_count(artist: str, count: int, lang: str):

    if lang == 'de':
        return (f'{artist} hatte *{str(count)}* Titel in der Hitparade')
