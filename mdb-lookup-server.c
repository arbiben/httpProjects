#include <stdio.h>      /* for printf() and fprintf() */
#include <sys/socket.h> /* for socket(), bind(), and connect() */
#include <arpa/inet.h>  /* for sockaddr_in and inet_ntoa() */
#include <stdlib.h>     /* for atoi() and exit() */
#include <string.h>     /* for memset() */
#include <unistd.h>     /* for close() */
#include "mdb.h"
#include <signal.h>

#define KeyMax 5
#define MAXPENDING 5    /* Maximum outstanding connection requests */

void DieWithError(char *errorMessage){  /* Error handling function */
    perror(errorMessage);
    exit(1);
}
void HandleTCPClient(int clntSocket);   /* TCP client handling function */

int main(int argc, char *argv[]){
    // ignore SIGPIPE so that we don’t terminate when we call
    // send() on a disconnected socket.
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR)
        DieWithError("signal() failed");

    int servSock;                    /* Socket descriptor for server */
    int clntSock;                    /* Socket descriptor for client */
    struct sockaddr_in echoServAddr; /* Local address */
    struct sockaddr_in echoClntAddr; /* Client address */
    unsigned short echoServPort;     /* Server port */
    unsigned int clntLen;            /* Length of client address data structure */

    if (argc != 3){     /* Test for correct number of arguments */
	fprintf(stderr, "Usage:  %s <Server Port>\n", argv[0]);
	exit(1);
    }
    
    echoServPort = atoi(argv[2]);  /* Second arg:  local port */
	                           
    /* Create socket for incoming connections */
    if ((servSock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
	DieWithError("socket() failed");			          
    
    /* Construct local address structure */
    memset(&echoServAddr, 0, sizeof(echoServAddr));   /* Zero out structure */
    echoServAddr.sin_family = AF_INET;                /* Internet address family */
    echoServAddr.sin_addr.s_addr = htonl(INADDR_ANY); /* Any incoming interface */
    echoServAddr.sin_port = htons(echoServPort);      /* Local port */
    
    /* Bind to the local address */
    if (bind(servSock, (struct sockaddr *) &echoServAddr, sizeof(echoServAddr)) < 0)
	DieWithError("bind() failed");
    
    /* Mark the socket so it will listen for incoming connections */
    if (listen(servSock, MAXPENDING) < 0)
	DieWithError("listen() failed");
    
    for (;;){ /* Run forever */	
        /* Set the size of the in-out parameter */
        clntLen = sizeof(echoClntAddr); 
    
        /* Wait for a client to connect */
        if ((clntSock = accept(servSock, (struct sockaddr *) &echoClntAddr, &clntLen)) < 0)
	    DieWithError("accept() failed");
    
        /* clntSock is connected to a client! */
        printf("connection started from [%s]\n", inet_ntoa(echoClntAddr.sin_addr));
        char *filename = argv[1];
        FILE *fp = fopen(filename, "rb");
        if (fp == NULL) DieWithError(filename);  
        FILE *input = fdopen(clntSock, "r");

        struct List list;
        initList(&list);

        int loaded = loadmdb(fp, &list);
        if (loaded < 0) DieWithError("loadmdb");
    
        fclose(fp);

        char line[1000];
        char key[KeyMax + 1];
    
        while (fgets(line, sizeof(line), input) != NULL) {
        // must null-terminate the string manually after strncpy().
            strncpy(key, line, sizeof(key) - 1);
            key[sizeof(key) - 1] = '\0';
        // if newline is there, remove it.
            size_t last = strlen(key) - 1;
            if (key[last] == '\n')
                key[last] = '\0';
        // traverse the list, printing out the matching records
            struct Node *node = list.head;
            int recNo = 1;
            while (node) {
                struct MdbRec *rec = (struct MdbRec *)node->data;
                if (strstr(rec->name, key) || strstr(rec->msg, key)) {
		    char str[57]= {0};
		    snprintf(str, 57, "%4d: {%s} said {%s}\n", recNo, rec->name, rec->msg);
		    send(clntSock, str, 57, 0); 
                }
                node = node->next;
                recNo++;
            }
	}
	    fprintf(stderr, "connection terminated from [%s]\n", inet_ntoa(echoClntAddr.sin_addr) );
	    fclose(input);
        
    // see if fgets() produced error
        if (ferror(input)) 
            DieWithError("input");

        freemdb(&list);
    }
}
