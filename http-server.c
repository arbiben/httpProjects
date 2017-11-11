#include <stdio.h>      /* for printf() and fprintf() */
#include <sys/socket.h> /* for socket(), bind(), and connect() */
#include <arpa/inet.h>  /* for sockaddr_in and inet_ntoa() */
#include <stdlib.h>     /* for atoi() and exit() */
#include <string.h>     /* for memset() */
#include <unistd.h>     /* for close() */
#include <sys/types.h>  /* for stat function */
#include <sys/stat.h>   /* for stat function */
#include <netdb.h>
#include <string.h>

#define MAXPENDING 5    /* Maximum outstanding connection requests */
#define bufSize 4096    /* readinf and writing default buffer size */
#define arrSize 1000    /* array size for char *s */

void HandleTCPClient(int clntSock, int hostSock, char *clntIP, char *webRoot); 
void DieWithError(char *errorMessage);    /* Server error handling function */
void errorMSG(int clntSock, char *msg); /* html error handling function */
const char *form();					// html format to send to client
const char *openHTML();					// html format to send to client 
const char *closeHTML();				// html format to send to client
const char *openTable();				// html format to send to client
const char *closeTable();				// html format to send to client
void printTableLine(int clntSock, char *mdbRec);	// html format to send to client
int color = 1;						// color indicator for HTMLtable

int main(int argc, char *argv[]){
    
    int servSock;                    /* Socket descriptor for server */
    int clntSock;                    /* Socket descriptor for client */
    int hostSock;		     /* Socket descriptor for hodt */
    struct sockaddr_inelizationchoServAddr; /* Local address */
    struct sockaddr_in echoClntAddr; /* Client address */
    struct sockaddr_in echoServAddr; /* Echo Server address */
    unsigned short echoServPort;     /* Server port */
    unsigned short echoClntPort;     /* Client Port */
    unsigned int clntLen;            /* Length of client address data structure */

    if (argc != 5){    /* Test for correct number of arguments */
        fprintf(stderr, "Usage:  %s <Server_Port> <web_root> <mdb-lookup-host> <mdb-lootup-port>\n", argv[0]);
        exit(1);
    }

    echoServPort = atoi(argv[1]);  /* First arg:  Server port HTTP request*/
    echoClntPort = atoi(argv[4]);  /* Fifth arg:  MdbLookup Port */
     
    /***********************************************/
    /* Establish connection with mdb-lookup server */
    /**********************************************/
    //Convert servName to IP #
    struct hostent *he;
    char *hostName = argv[3];
    //get server ip from server name
    if ((he = gethostbyname(hostName)) == NULL)
        DieWithError("gethostbyname failed");
     char *servIP = inet_ntoa(*(struct in_addr *)he->h_addr);

    // Create a realiable stream socket using TCP - connecting to MDB_LOOKUP
    if ((hostSock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
	DieWithError("Client socket() failed");
    
    // Construct the server address structure 
    memset(&echoServAddr, 0, sizeof(echoServAddr));     // Zero out structure
    echoServAddr.sin_family      = AF_INET;             // Internet address family
    echoServAddr.sin_addr.s_addr = inet_addr(servIP);   // Server IP address
    echoServAddr.sin_port        = htons(echoClntPort); // Server port 
    
    // Establish the connection to the echo server
    if (connect(hostSock, (struct sockaddr *) &echoServAddr, sizeof(echoServAddr)) < 0    )
        DieWithError("connect() to mdb-lookup failed");
    
    /* Connected to mdb-lookup! */
    
    /*******************************************************/
    /* From this point - Socket for incoming http requests */
    /*******************************************************/

    // Create socket for incoming connections 
    if ((servSock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
        DieWithError("Server socket() failed");
      
    // Construct local address structure 
    memset(&echoServAddr, 0, sizeof(echoServAddr));   // Zero out structure 
    echoServAddr.sin_family = AF_INET;                // Internet address family 
    echoServAddr.sin_addr.s_addr = htonl(INADDR_ANY); // Any incoming interface 
    echoServAddr.sin_port = htons(echoServPort);      // Local port 

    // Bind to the local address 
    if (bind(servSock, (struct sockaddr *) &echoServAddr, sizeof(echoServAddr)) < 0)
        DieWithError("bind() failed");

    // Mark the socket so it will listen for incoming connections 
    if (listen(servSock, MAXPENDING) < 0)
        DieWithError("listen() failed");

    for (;;) // Run forever 
    {
        // Set the size of the in-out parameter 
        clntLen = sizeof(echoClntAddr);

        // Wait for a client to connect 
        if ((clntSock = accept(servSock, (struct sockaddr *) &echoClntAddr, 
                               &clntLen)) < 0)
            DieWithError("accept() failed");

        // clntSock is connected to a client! 

        HandleTCPClient(clntSock, hostSock, inet_ntoa(echoClntAddr.sin_addr), argv[2]);
    }
    /* NOT REACHED */
}

void HandleTCPClient(int clntSocket, int hostSocket, char *clntIP, char *root){

/*****************************************/
/*           Handle TCP Client           */
/*****************************************/

    FILE *clntSock = fdopen(clntSocket, "r");
    char requestLine[arrSize] = {0}; // content received from client
    char serverMSG[arrSize] = {0};   // contant that will be presented on server side
    char webRoot[arrSize] = {0};
    char buf[bufSize];

    strcpy(webRoot, root);
 
    // if browser crashes
    if(!fgets(requestLine, sizeof(requestLine), clntSock)){
	fprintf(stdout, "%s \"  \" 400 Bad Request\n", clntIP);
	close(clntSocket);
	return;
    }

    // seperates request line to tokens
    char *token_separators = "\t \r\n"; // tab, space, new line
    char *method = strtok(requestLine, token_separators);// GET
    char *requestURI = strtok(NULL, token_separators);   // PATH
    char *httpVersion = strtok(NULL, token_separators);  // HTTP/1.1 / HTTP/1.0
    
    snprintf(serverMSG, arrSize, "%s \"%s %s %s\"", clntIP, method, requestURI, httpVersion);
    
    // check if number of inputs is valid
    // if httpV is NULL it means that one or more
    // of the variables havent been inputed 
    if (httpVersion == NULL){
	errorMSG(clntSocket, "HTTP/1.0 501 Not Implemented\n\n");
	fprintf(stdout, "%s 501 Not Implemented\n", serverMSG);
	close(clntSocket);
	return;
    }
    
    //add argv[2] to the requestURI
    strcat(webRoot, requestURI);

    // check if the METHOD is get - otherwise close socket
    if (strncmp(method, "GET", 3)){
        errorMSG(clntSocket, "HTTP/1.0 501 Not Implemented\n\n");
	fprintf(stdout, "%s 501 Not Implemented\n", serverMSG);
	close(clntSocket);
	return;
    }

    // check if HTTP version is 1.0 or 1.1 - otherwise close socket
    httpVersion += strlen(httpVersion) - 8; // move pointer to last 8 chars
    if (strcmp(httpVersion, "HTTP/1.1") != 0 && strcmp(httpVersion, "HTTP/1.0") != 0){
	errorMSG(clntSocket, "HTTP/1.0 501 Not Implemented\n\n");
	fprintf(stdout, "%s 501 Not Implemented\n", serverMSG);
	close(clntSocket);
	return;
    }

    // checking if requestURI begins with / - otherwise close socket
    if (*requestURI != '/'){
	errorMSG(clntSocket, "HTTP/1.0 400 Bad Request\n\n");
	fprintf(stdout, "%s 400 Bad Request\n", serverMSG);
	close(clntSocket);
	return;
    }

    // checking if path contains ../ or /../ - if so closes socket
    if((strstr(requestURI, "/..")) != NULL ){
	errorMSG(clntSocket, "HTTP/1.0 400 Bad Request\n\n");
	fprintf(stdout, "%s 400 Bad Request\n", serverMSG);
	close(clntSocket);
	return;
    }

    // if requestURI(which is now webRoot) end with / - add index.html by default
    if (webRoot[strlen(webRoot)-1] == '/')
	strcat(webRoot,"index.html");
    
    // checks if path ends with diectory - if so adds /index.html
    struct stat s={};
    stat(webRoot, &s); 
    if(S_ISDIR(s.st_mode)) 
	strcat(webRoot, "/index.html");

    // check if requestURI ends with /mdb-lookup
    char *last = strrchr(requestURI, '/');
    
    // preparing positive output
    strcat(serverMSG, " 200 OK");
    
    char *okMSG = "HTTP/1.0 200 OK\n\n";
   
    // checks if page at the end of requestURI exsists - if not closes socket
    FILE *fp = fopen(webRoot, "r");
    if(fp == NULL && (strncmp(last, "/mdb-lookup", 11) != 0)){
	errorMSG(clntSocket, "HTTP/1.0 404 Not Found\n\n");
	fprintf(stdout, "%s 404 Not Found\n", serverMSG);
	close(clntSocket);
	return;
    } 
    for(;;){
	char input[arrSize] = {0};
        fgets(input, sizeof(input), clntSock);
	if((strcmp("\r\n", input) == 0) || (input[0] == '\n')) break;
    }
    
    if(fp){
        int size;
        send(clntSocket, okMSG, strlen(okMSG), 0); 
	while((size = fread(buf, 1, bufSize, fp)))
	    send(clntSocket, buf, size, 0);
        
	fprintf(stdout, "%s\n", serverMSG);
       
	fclose(fp);
	close(clntSocket);
	return;
    }
    else{
        send(clntSocket, okMSG, strlen(okMSG), 0); 
	char mdbForm[bufSize] = {0};
	snprintf(mdbForm, bufSize, "%s %s", openHTML(), form());
	send(clntSocket, mdbForm, strlen(mdbForm), 0);
	
	char *key;
	key = strrchr(requestURI, '=');

	if (key++ == NULL){
	    send(clntSocket, closeHTML(), strlen(closeHTML()), 0);
	    fprintf(stdout, "%s\n", serverMSG);
	    close(clntSocket);
	    return;
	}
	else{
            FILE *mdbSock = fdopen(hostSocket, "r+");
	    
	    fprintf(stdout, "looking up [%s]: %s\n", key, serverMSG);
	    strcat(key, "\n");
	    send(hostSocket, key, strlen(key), 0);
	    send(clntSocket, openTable(), strlen(openTable()), 0);    
	    
	    while(strlen(fgets(buf, arrSize, mdbSock))>1){
		printTableLine(clntSocket,buf);
	    }
	    
	    send(clntSocket, closeTable(), strlen(closeTable()), 0);
	    send(clntSocket, closeHTML(), strlen(closeHTML()), 0);
	    
	    close(clntSocket);
	    return;
	}
    }
    //** NEVER REACHED **//
    return;
}

/***************************************/
/*         ALL HTML COMMANDS           */
/***************************************/

const char *form(){
    const char *lookup = 
	"\r<h1>mdb-lookup</h1>\n"
        "\r<p>\n"
        "\r<form method=GET action=/mdb-lookup>\n"
        "\rlookup: <input type=text name=key>\n"
        "\r<input type=submit>\n"
        "\r</form>\n"
        "\r<p>\n";
    
    return lookup;
}

const char *openHTML(){
    return "<html>\n    <body>\n";
}

const char *closeHTML(){
    return "\n    </body>\n</html>\n";
}

const char *openTable(){
    return "    <p><table border>";
}

const char *closeTable(){
    return "    </table>";
}

void printTableLine(int clntSock, char *mdbRec){
    char value[arrSize] = {0};
    if (color==1) snprintf(value, arrSize, "<tr><td>%s</td></tr>\n", mdbRec);
    else snprintf(value, arrSize, "<tr><td bgcolor=\"B4D8E7\">%s</td></tr>\n", mdbRec);
    
    send(clntSock, value, strlen(value),0);
    color*=-1;
    return;
}

void errorMSG(int clntSock, char *msg){
    char msgOut[arrSize] = {0};  
    send(clntSock, msg, strlen(msg), 0);
    msg+=9;
    snprintf(msgOut, bufSize, "\n%s<h1>%s</h1>%s\n",openHTML(), msg, closeHTML());
    send(clntSock, msgOut, strlen(msgOut), 0);
    return;
}

void DieWithError(char *errorMessage){
    fprintf(stdout,"%s\n", errorMessage);
    exit(1);
}
