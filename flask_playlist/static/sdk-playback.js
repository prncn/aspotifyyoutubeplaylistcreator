window.onSpotifyWebPlaybackSDKReady = () => {
    const player = new Spotify.Player({
        name: 'Tubify Playback',
        getOAuthToken: cb => { cb(token); },
        volume: 0.3
    });

    player.connect().then(success => {
      if (success) {
        // console.log('The Web Playback SDK successfully connected to Spotify!');
      }
    })

    player.addListener('ready', data => {
        // console.log('The Web Playback SDK is ready to play music!');
        // console.log('Device ID', data.device_id);
        $('body').bind('touchstart', function() {});
        $('.playlist')
            .on('mouseenter touchstart', function (e) {
                //console.log(this.href)
                play(data.device_id, this.href)
                e.stopPropagation()
                //e.preventDefault()
            })
            .on('mouseleave touchend', function (e) {
                //e.preventDefault()
                player.pause()
            });
    })
};


function play(device_id, uri) {
$.ajax({
    url: "https://api.spotify.com/v1/me/player/play?device_id=" + device_id,
    type: "PUT",
    data: '{"context_uri": "'+uri+'", "position_ms": 25000}',
    beforeSend: function (xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + token);
    },
});}

function pause() {
$.ajax({
    url: "https://api.spotify.com/v1/me/player/pause",
    type: "PUT",
    beforeSend: function (xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + token);
    },
});}