#include <gps.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <strings.h>

#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>

const char *gpsNodeName;

/* keep the data available between losses of GPS fix */
double distance = 0;
int isPrevValid = 0;
struct gps_fix_t prev;

/* socket stuff */
int sockfd;
socklen_t salen;
struct sockaddr *sa;

int create_udp_socket(const char *host, const char *port)
{
    struct addrinfo hints, *res;
    int n;

    /*initilize addrinfo structure*/
    bzero(&hints, sizeof(struct addrinfo));  
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_protocol = IPPROTO_UDP;

    if((n = getaddrinfo(host, port, &hints, &res)) != 0)
        printf("UDP getaddrinfo error for %s, %s: %s", host, port, gai_strerror(n));

    do {
        sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
        if(sockfd >= 0)
            break; /*success*/
    } while ((res = res->ai_next) != NULL);

    sa = (sockaddr*) malloc(res->ai_addrlen);
    memcpy(sa, res->ai_addr, res->ai_addrlen);
    salen = res->ai_addrlen;

    freeaddrinfo(res);

    if (sockfd < 0) {
        printf("Error: Could not create a socket to %s:%s\n", host, port);
        exit(1);
    }

    return sockfd;
}

void logDataOut(struct gps_fix_t *fix)
{
    char buffer[1000];
    double distance_km = distance / 1000.0;
    double speed_kmh = fix->speed * 3.6;
    int rc;

    printf("timestamp: %.0f, latitude: %f, longitude: %f, altitude: %f, speed: %f km/h, distance: %f km\n", 
           fix->time, fix->latitude, fix->longitude, fix->altitude,
           speed_kmh, distance_km);

    int len = snprintf(buffer, sizeof(buffer), "%s\t%.0f\t%f\t%f\t%f\t%f\t%f\n",
                       gpsNodeName, fix->time, distance_km,  fix->latitude,
                       fix->longitude, fix->altitude, speed_kmh);

    if( (rc = sendto(sockfd, buffer, len, 0, sa, salen)) < 0 ) {
        perror("sending datagram");
    }
}

bool mainLoop(struct gps_data_t *gps_data, int sockfd)
{
    int rc;

     while (1) {
        /* wait for 2 seconds to receive data */
        if (gps_waiting (gps_data, 2000000)) {
            /* read data */
            if ((rc = gps_read(gps_data)) == -1) {
                return false;
            } else {
                /* Display data from the GPS receiver. */
                if ((gps_data->status == STATUS_FIX) && 
                    (gps_data->fix.mode == MODE_2D || gps_data->fix.mode == MODE_3D) &&
                    !isnan(gps_data->fix.latitude) &&
                    !isnan(gps_data->fix.longitude)) {
                        if (isPrevValid) {
                            distance += earth_distance(prev.latitude, 
                                                       prev.longitude,
                                                       gps_data->fix.latitude,
                                                       gps_data->fix.longitude);
                        }

                        logDataOut(&gps_data->fix);

                        prev = gps_data->fix;
                        isPrevValid = 1;
                } else {
                    printf("no GPS data available\n");
                }
            }
        }
    }

    return true;
}

int main(int argc, char **argv) {
    bool res;
    int rc;

    /* check the parameters */
    if (argc != 4) {
        fprintf(stderr, "Usage: %s nodeName host port\n", argv[0]);
        exit(1);
    }

    /* Use the parameters */
    gpsNodeName = argv[1];
    int sockfd = create_udp_socket(argv[2], argv[3]);

    do {
        struct gps_data_t gps_data;
        if ((rc = gps_open("localhost", "2947", &gps_data)) == -1) {
            printf("code: %d, reason: %s\n", rc, gps_errstr(rc));
            return EXIT_FAILURE;
        }
        gps_stream(&gps_data, WATCH_ENABLE | WATCH_JSON, NULL);

        res = mainLoop(&gps_data, sockfd);

        /* When you are done... */
        gps_stream(&gps_data, WATCH_DISABLE, NULL);
        gps_close (&gps_data);
    } while (res == false);

    return EXIT_SUCCESS;
}
