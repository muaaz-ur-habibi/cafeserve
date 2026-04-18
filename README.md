<h1 align="center">CafeServe</h1>
<h3 align="center">A simple LAN server program</h3>
<hr>
<h2>Overview</h2>
<p>
  This is a simple LAN server designed for home usage. It includes storage, media viewing and sharing services.
</p>
<hr>
<h2>Setup</h2>
<p>
  To run cafeserve in a production ready environment, you must first install a suitable WSGI server for your O.S: for Windows use <a href="https://github.com/Pylons/waitress">Waitress</a>,
  for Linux or Mac use <a href="https://github.com/benoitc/gunicorn">Gunicorn</a>

  To install them, run the following commands:<br>
  Gunicorn:
  ```
  pip install gunicorn
  ```
  Waitress:
  ```
  pip install waitress
  ```
  <br><br>
  Next install cafeserve
  ```
  git clone https://github.com/muaaz-ur-habibi/cafeserve --depth=1
  ```
  <br>
  To run:
  ```
  (waitress-serve or gunicorn) cafeserve.py
  ```
</p>
