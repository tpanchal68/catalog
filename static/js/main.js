function start() {
    gapi.load('auth2', function() {
        auth2 = gapi.auth2.init({
        client_id: '301408615627-fh6eheqj6bl95tn83vupc1ohl23s9049.apps.googleusercontent.com'
        });
    });
}
