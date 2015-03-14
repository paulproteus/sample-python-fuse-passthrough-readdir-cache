ldpreload.so: ldpreload.c
	gcc -Wall -fPIC -shared -o ldpreload.so ldpreload.c -ldl
