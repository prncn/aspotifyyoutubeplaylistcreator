# spotify-playlist-api

Built in Flask. This web app fetches data from your linked Spotify account and Google account. You can then view some unique listening statistics, view an alternate minimal Spotify Player (previews your recently created playlists), and also add your recently liked Songs from YouTube into a Spotify playlist (idea taken from a python script).

The account linking directs through Google OAuth and Spotify Login respectively. The data on the artists' gender is a guess by referencing the list of artists to last.fm (request to the artist's bio) and then checking that text for pronouns (works pretty well for solo artists).

This has been deployed to http://aintshitsweet.pythonanywhere.com/ to test out.
