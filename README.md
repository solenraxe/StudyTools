TECH STACK: Made using Python, more specifically using the Pygame library. Also uses the sys, os, json and datetime libraries.
No AI was used for this specific project (neither debugging nor coding), although some parts coming from a previous project might have been debugged using AI

I started university this year, and to my surprise they didn't give out any kind of timetable, just big chunky boards where you have to spend 5 minutes finding what your next class is...
So I wanted to install an app for that, but I couldn't find a satisfying one, they were all either locked behind a paywall (eww) or incomplete and filled with ads every 5 seconds (yuck)
Following this, like any normal person, I just decided to make my own in Python.

I also decided to include a to do list, because I'd never made one and I'm just cool like that (and needed one too)
I also wanted to make flashcards but got bored of this project before I could even start

When opening the app, you can either go to the timetable tab or the to do list one, I might add more in the future...

<img width="800" height="632" alt="image" src="https://github.com/user-attachments/assets/45f9ce0d-ca74-4a4a-8fce-9627e3be9513" />

In the timetable tab, you will see a timetable with all the events of the current week, starting by Monday. You can view the events for other weeks too by clicking the arrows on top of the screen.
By clicking the "Add event" button in this tab, you will be able to select a date, a time, a name and a duration for your event, along with a color and if it should repeat or not.
You can also edit existing event by clicking on them in the timetable, it'll automatically fill in the fields so you don't have to re-input everything every time you want to change the color.
Pressing Enter while adding/editing an event will create/modify it and write it to the json file, Tab makes you go back without any changes and Del deletes the event you're modifying.
Events that have already passed are automatically erased from the json file.

<img width="800" height="632" alt="image" src="https://github.com/user-attachments/assets/dee54485-1981-4c84-9242-64f2ab9bfbe0" />

The to do list is fairly simple, and you've probably reviewed dozens by now, so I'm gonna keep it simple.
You can add and modify tasks just like the events in the timetable tab, tasks that you have completed or were due for a previous date are automatically deleted from the json file
Completing a task makes it green to give you a tiny bit of satisfaction (yay)
If you have too many tasks for them to show all at once, a scroll bar will show up and you'll be able to scroll using your mouse wheel/touchpad (pretty proud of that)

<img width="800" height="632" alt="image" src="https://github.com/user-attachments/assets/240d5e02-9c72-43bc-8255-28e1d13bd131" />

To try out the project, just download the .zip corresponding to your OS, extract it and double click the file inside (.exe on windows)
Only supports Linux and Windows, sorry MacOS
