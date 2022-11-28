%%% Two lamps example
%%% (C) 2022, F. Wotawa

% Program responsible for handling the not abnormal and abnormal predicate for all components. 

comp(X) :- type(X,T).

nab(X) :- comp(X), not ab(X).
ab(X) :- comp(X), not nab(X).

% Counting the number of abnormal predicates in a solution

no_ab(N) :- N = #count { C : ab(C) }. % Use a different name in the book. 
				    % Adapted to work together with the current implementation

% ADD IF NEEDED WHEN ONLY USING CLINGO
%:- not no_ab(1).

% Nominal behavior of the components

val(pow(X),nominal) :- type(X,bat), nab(X).

val(out_pow(X),V) :- type(X,sw), on(X), val(in_pow(X),V), nab(X).
val(in_pow(X),V) :- type(X,sw), on(X), val(out_pow(X),V), nab(X).
val(out_pow(X),zero) :- type(X,sw), off(X), nab(X).

val(light(X),on) :- type(X,lamp), val(in_pow(X),nominal), nab(X).
val(light(X),off) :- type(X, lamp), val(in_pow(X),zero), nab(X).
val(in_pow(X), nominal) :- type(X,lamp), val(light(X),on).

% Structural descriptions

val(X,V) :- conn(X,Y), val(Y,V). 
val(Y,V) :- conn(X,Y), val(X,V).

:- val(X,V), val(X,W), not V=W. 

% Only report the health states
% Add this information to your particular system

%#show ab/1.
%#show nab/1.
%#show val/2.
%#show on/1.
%#show off/1.

% Test system

type(b, bat).
type(s, sw).
type(l1, lamp).
type(l2, lamp).

conn(in_pow(s), pow(b)).
conn(out_pow(s), in_pow(l1)).
conn(out_pow(s), in_pow(l2)).


% Observations
% MAYBE REMOVED WHEN USING IN A DIFFERENT CONTEXT
		      
%off(s).
%val(light(l1),on(s)).
%val(light(l2),on(s)).


