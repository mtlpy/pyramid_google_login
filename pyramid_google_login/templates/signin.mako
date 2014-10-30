<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Signin</title>
  </head>
  <body>
    <p style="text-align: center; font-size: 2em; font-family: arial;">
        <a href="${signin_redirect_url}">Signin on Google!</a>
    </p>

    % if message:
    <p style="text-align: center; font-family: arial;">
        ${message}
    </p>
    % endif
  </body>
</html>
