#include <stdio.h>      /* for printf() and fprintf() */
#include <sys/socket.h> /* for socket(), connect(), send(), and recv() */
#include <arpa/inet.h>  /* for sockaddr_in and inet_addr() */
#include <stdlib.h>     /* for atoi() and exit() */
#include <string.h>     /* for memset() */
#include <unistd.h>     /* for close() */
#include <netdb.h>
#include <sys/types.h>
#include <string.h>

#define RCVBUFSIZE 1000   /* Size of receive buffer */

void DieWithError(char *errorMessage){  /* Error handling function */
    perror(errorMessage);
    exit(1);
}

int main(int argc, char *argv[])
{
    int sock;                        /* Socket descriptor */
    struct sockaddr_in echoServAddr; /* Echo server address */
    unsigned short echoServPort;     /* Echo server port */
    char *servIP;                    /* Server IP address (dotted quad) */
    char echoString[1000];           /* String to send to echo server */

    if (argc != 4){    /* Test for correct number of arguments */
       fprintf(stderr, "Usage: %s <Host> <Port_Number> <File_Path>\n",
               argv[0]);
       exit(1);
    }

    //Convert servName to IP #
    struct hostent *he;
    char *serverName = argv[1];
    // get server ip from server name
    if ((he = gethostbyname(serverName)) == NULL)
	DieWithError("gethostbyname failed");
    servIP = inet_ntoa(*(struct in_addr *)he->h_addr);
    echoServPort = atoi(argv[2]);

    /* Create a reliable, stream socket using TCP */
    if ((sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
        DieWithError("socket() failed");

    /* Construct the server address structure */
    memset(&echoServAddr, 0, sizeof(echoServAddr));     /* Zero out structure */
    echoServAddr.sin_family      = AF_INET;             /* Internet address family */
    echoServAddr.sin_addr.s_addr = inet_addr(servIP);   /* Server IP address */
    echoServAddr.sin_port        = htons(echoServPort); /* Server port */

    /* Establish the connection to the echo server */
    if (connect(sock, (struct sockaddr *) &echoServAddr, sizeof(echoServAddr)) < 0)
        DieWithError("connect() failed");
    
    // copy to echoString and send to socket    
    snprintf(echoString, RCVBUFSIZE, "GET %s HTTP/1.0\r\nHost: %s:%d\r\n\r\n", argv[3],argv[1],echoServPort);

    FILE *s = fdopen(sock, "r");
    send(sock, echoString, strlen(echoString),0); 
    
    char inputStr[1000];
    fgets(inputStr, RCVBUFSIZE, s);
    if(strncmp(inputStr, "HTTP/1.1 2",10) != 0){
	printf("%s\n", inputStr);
	exit(1);
    } 
    
    // while returning headers do nothing
    while(fgets(inputStr, RCVBUFSIZE, s)[0] != '\r');

    // after headers - creat file and copy all input to that file
    char *fn = strrchr(argv[3], 47);
    FILE *f = fopen(++fn, "w+");

    size_t n; 
    while((n = fread(inputStr, 1, RCVBUFSIZE, s)) > 0){
	if (fwrite(inputStr, 1, n, f) != n)
	    DieWithError("fwrite failed");
    }

    fclose(f);
    fclose(s);

    return(0);
}
