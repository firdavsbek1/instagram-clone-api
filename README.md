# instagram-clone-api
Created the API for Instagram Like App

Built Api for Instagram Like Application where all the basic concepts are included. Most importantly The Authentication is well planned: divided into different stages and 
this way user can be handled when he is at some stage and phone turnof or just leave application. A way to track user authentication status is implemented. Validations for 
all the fields are well written in the serializers so that database would be kept free and clean.                                                                    
-------------- Concepts Implemented----------------------                                                                                                            
1.CustomUser Model -> change to USER_AUTH_MODEL                                                                                                            
2.Authentication & Authorization -> 401 & 403 Errors are made use of.                                                                                                 
3.Sending Email with Threading(Asynchronous programming)                                                                                                            
4.Code verification From email/sms message                                                                                                            
5.Phone/Email/Username regex for validation                                                                                                            
6.Forgot Password/Change Password included                                                                                                            
7.Generating Refresh/Access Tokens(through simple_jwt)                                                                                                            
8.Full CRUD on Post/Comment                                                                                                                                          
9.DB design for post like and comment like                                                                                                                           
10.DB desing for replying to specific person's comment                                                                                                                
11.Custom Pagination(PageNumberPagination)                                                                                                                      
