from .settings import CLIENT_ID, API_LOCATION, SWAP_TOKEN_ENDPOINT, SUCCESS_ROUTE, ERROR_ROUTE

google_login_javascript_client = f"""<!DOCTYPE html>
<html itemscope itemtype="http://schema.org/Article">
<head>
    <meta charset="UTF-8">
    <meta name="google-signin-client_id" content="{CLIENT_ID}">
    <title>Google Login</title><script src="https://apis.google.com/js/platform.js" async defer></script>
    <body>
    <div class="g-signin2" data-onsuccess="onSignIn"></div>
    <script>function onSignIn(googleUser) {{
  
  var id_token = googleUser.getAuthResponse().id_token;
    var xhr = new XMLHttpRequest();
xhr.open('POST', '{API_LOCATION}{SWAP_TOKEN_ENDPOINT}');
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
xhr.setRequestHeader('X-Google-OAuth2-Type', 'client');
xhr.onload = function() {{
   console.log('Signed in as: ' + xhr.responseText);
}};
xhr.send(id_token);
}}</script>
<div><br></div>
<a href="#" onclick="signOut();">Sign out</a>
<script>
  function signOut() {{
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {{
      console.log('User signed out.');
    }});
  }}
</script>
</body>
</html>"""

google_login_javascript_server = f"""<!DOCTYPE html>
<html itemscope itemtype="http://schema.org/Article">
<head>
    <meta charset="UTF-8">
    <title>Google Login</title>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js">
    </script>
    <script src="https://apis.google.com/js/client:platform.js?onload=start" async defer>
    </script>
    <script>
    function start() {{
      gapi.load('auth2', function() {{
        auth2 = gapi.auth2.init({{
          client_id: '{CLIENT_ID}',  
          // Scopes to request in addition to 'profile' and 'email'
          // scope: 'additional_scope'
        }});
      }});
    }}
  </script>
</head>
<body>
<button id="signinButton">Sign in with Google</button>
<script>
  $('#signinButton').click(function() {{
    // signInCallback defined in step 6.
    auth2.grantOfflineAccess().then(signInCallback);
  }});
</script>
<script>
function signInCallback(authResult) {{
  if (authResult['code']) {{
    // Hide the sign-in button now that the user is authorized, for example:
    $('#signinButton').attr('style', 'display: none');
    // Send the code to the server
    $.ajax({{
      type: 'POST',
      url: '{API_LOCATION}{SWAP_TOKEN_ENDPOINT}',
      // Always include an `X-Requested-With` header in every AJAX request,
      // to protect against CSRF attacks.
      headers: {{
        'X-Requested-With': 'XMLHttpRequest',
        'X-Google-OAuth2-Type': 'server'
      }},
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {{
          location.href = '{API_LOCATION}{SUCCESS_ROUTE}'
        // Handle or verify the server response.
      }},
      processData: false,
      data: authResult['code']
    }});
  }} else {{
    // There was an error.
    console.log(e)
    location.href = '{API_LOCATION}{ERROR_ROUTE}'
  }}
}}
</script>
</body>
</html>"""