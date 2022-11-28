%
% Heating system model
%
% (C) 2021, F. Wotawa, TU Graz, Institute for Software Technology

% Definition of temperature model
% Pre-definition of the temperature range

next(between(t_max,t_up),t_max).
next(t_up,between(t_max,t_up)).
next(between(t_up,t_low), t_up).
next(t_low,between(t_up,t_low)).
next(between(t_low,null),t_low).
next(null, between(t_low,null)).

greater(X,Y) :- next(Y,X).
greater(X,Y) :- next(Z,X), greater(Z,Y).

smaller(X,Y) :- next(X,Y).
smaller(X,Y) :- next(X,Z), smaller(Z,Y).

inc(X,Y) :- next(X,Y), X != t_max.
inc(t_max,t_max).

dec(X,Y) :- next(Y,X), X != null.
dec(null, null).

% Determining the value of temperature using the predicate val(port, value, time)

val(int(S), Z, T+1) :- type(S,temp), val(in(S), V, T), val(int(S), W, T), greater(V,W), inc(W,Z).
val(int(S), Z, T+1) :- type(S,temp), val(in(S), V, T), val(int(S), W, T), smaller(V,W), dec(W,Z).
val(int(S), V, T+1) :- type(S,temp), val(in(S), V, T), val(int(S), V, T).

%%% Handling time

time(0).
time(T+1) :- time(T), T < 10.

%%% Diagnosis model

comp(X) :- type(X,_).

nab(X) :- comp(X), not ab(X).
ab(X) :- comp(X), not nab(X).

no_ab(N) :- N = #count { C : ab(C) }.

:- not no_ab(1). % Search for single faults only

% Switch model

tuple(switch, max, max).
tuple(switch, half, half).
tuple(switch, null, null).

val(out(S), W, T) :- type(S, switch), nab(S), on(S,T), val(in(S), V, T), tuple(switch, V, W).
val(in(S), W, T) :- type(S, switch), nab(S), on(S,T), val(out(S), V, T), T>0, tuple(switch, V, W).
val(out(S), null, T) :- type(S, switch), nab(S), off(S,T).
%val(out(S), null, T) :- type(S, switch), ab(S), time(T). % Fault model

:- on(S,T), off(S,T).

% Heater model

tuple(heater, max, t_max).
tuple(heater, half, t_low).
tuple(heater, null, null).

val(out(H), W, T) :- type(H, heater), nab(H), val(in(H), V ,T), tuple(heater, V, W).
val(out(H), null, T) :- type(H, heater), ab(H), time(T). % Fault model

% Battery model (delivering maximum current)

val(out(B), max, T) :- type(B, battery), nab(B), time(T).
val(out(B), half, T); val(out(B),null,T) :- type(B, battery), ab(B), time(T). % Fault model

% Connections

val(Y,V,T) :- conn(X,Y), val(X,V,T).
val(X,V,T) :- conn(X,Y), val(Y,V,T).

:- val(Y,V,T), val(Y,W,T), W!=V.

% Structure

type(sw, switch).
type(h, heater).
type(tm,temp).
type(bat, battery).

conn(out(bat),in(sw)).
conn(out(sw),in(h)).
conn(out(h),in(tm)).

% Controller behavior

on(sw,T+1) :- val(int(tm),V,T), smaller(V,t_up).
off(sw,T+1) :- val(int(tm),V,T), greater(V,t_up).
off(sw,T+1) :- val(int(tm),t_up,T).  
off(sw,0).

% Observations
%val(int(tm),null,0). % At the beginning there is no heat stored
%val(out(bat),max,0).
%val(int(tm),t_low,0).
%val(out(bat),max,0).
%val(out(sw),null,0).
%val(out(h),null,0).

%val(int(tm),t_up,1).
%val(int(tm),between(t_up,t_low),2).
%off(sw,1).
%off(sw,2).
%val(out(bat),max,1).
%val(out(bat),max,2).
%val(in(h),t_max,1).
%val(in(h),t_max,2).
%val(out(sw), null, 1).
%val(out(sw), null, 2).

%val(int(tm),between(t_up,t_low),1).
%val(out(bat),max,1).
%val(out(sw),max,1).
%val(out(h),t_max,1).

% val(int(tm),t_up,2).
% val(out(bat),max,2).
% val(out(sw),max,2).
% val(out(h),t_max,2).

%val(int(tm),null,0). % At the beginning there is no heat stored

%val(int(tm),null,1).
%val(int(tm),between(t_low,null),2). 
%val(int(tm),t_low,3). 
%val(int(tm),t_low,4). 
%val(int(tm),t_low,5).
%val(int(tm),t_low,6).
%val(int(tm),t_low,7). 
%val(int(tm),t_low,8).
%val(int(tm),t_low,9).
%val(int(tm),t_low,10). 
%val(int(tm),t_low,11). 
%val(int(tm),t_low,12). 
%val(int(tm),t_low,13).
%val(int(tm),t_low,14).
%val(int(tm),t_low,15).
%val(int(tm),t_low,16).

%val(int(tm),null,1).
%val(int(tm),between(t_low,null),2). 
%val(int(tm),t_low,3). 
%val(int(tm),between(t_up,t_low),4).
%val(int(tm),t_up,5).
%val(int(tm),between(t_max,t_up),6).
%val(int(tm),t_up,7). 
%val(int(tm),between(t_up,t_low),8).
%val(int(tm),t_low,9).
%val(int(tm),between(t_up,t_low),10). 
%val(int(tm),t_up,11). 
%val(int(tm),between(t_max,t_up),12). 
%val(int(tm),t_up,13).
%val(int(tm),between(t_up,t_low),14).
%val(int(tm),t_low,15).
%val(int(tm),between(t_up,t_low),16).

% Display values of temperature only
%#show val/3.
%#show on/2.
%#show off/2.
%#show nab/1.
#show ab/1.