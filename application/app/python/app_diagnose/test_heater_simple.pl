% Simple temperature model comprising an external temperature input and a system 
% with an internal temperature. To be used as example for heating simulation.
% (C) 2021, F. Wotawa, TU Graz, Institute for Software Technology

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

val(int(S), Z, T+1) :- val(in(S), V, T), val(int(S), W, T), greater(V,W), inc(W,Z).
val(int(S), Z, T+1) :- val(in(S), V, T), val(int(S), W, T), smaller(V,W), dec(W,Z).
val(int(S), V, T+1) :- val(in(S), V, T), val(int(S), V, T).

%%% Diagnosis model
type(tm,temp).
type(sw, switch).

comp(X) :- type(X,_).

nab(X) :- comp(X), not ab(X).
ab(X) :- comp(X), not nab(X).

no_ab(N) :- N = #count { C : ab(C) }.

% Observations

% Display values of temperature only

%#show val/3.
#show ab/1.
