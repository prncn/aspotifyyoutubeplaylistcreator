# Tubify: Spotify API Web App
This flask web app lets the user connect their YouTube and Spotify to access three functions.  
The "login" is handled by a Google OAuth Login and Spotify's authentication.  
  

### Create a Playlist 
This function sends the user through Google OAuth. It fetches a number of recent Likes on  
YouTube (music) videos and YouTube Music songs. The collected songs are then used to create  
a new playlist on the user's connected Spotify account. Use this if you want to import your recent  
YouTube music to Spotify.

### Your favorites, by gender
This function collects various artists' data from the connected Spotify account. Its main goal  
is to try to determine some statistics on the user's listening behaviour that is not easily accessible,  
like the user's gender bias. *(left unfinished)*

### Display your collection
This function creates a display of the user's playlist. A snippet preview of a playlist  
thumbnail is played on mouse hover.

#### Known Problems
*Due to YouTube's ever changing functionalities and web page, it's impossible to reliably fetch song information  
on liked videos. As of now, some videos that should contain song information should be detected while  
others will not.*
  
*DEMO:* https://aintshitsweet.pythonanywhere.com/
