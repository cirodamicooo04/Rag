% Retrieval quality, trust, source diversity and retry strategy.

usable_chunk(C) :- retrieved(C), retrieval_score(C,S), min_retrieval_score(M), S >= M,
                   document_trust(C,T), min_document_trust(MT), T >= MT,
                   chunk_security(C,safe).

usable_count(N) :- N = #count { C : usable_chunk(C) }.
trusted_source(S) :- usable_chunk(C), chunk_source(C,S).
source_count(N) :- N = #count { S : trusted_source(S) }.

sufficient_context :- usable_count(N), min_usable_chunks(M), N >= M.
weak_context :- not sufficient_context.
single_source_context :- sufficient_context, source_count(1).
contradictory_context :- context_consistency(contradictory).

candidate_action(generate) :- sufficient_context.
candidate_action(retrieve_again) :- weak_context, retrieval_attempt(A), max_retrieval_attempts(M), A < M.
candidate_action(return_insufficient_context) :- weak_context, retrieval_attempt(A), max_retrieval_attempts(M), A >= M.
candidate_action(human_review) :- contradictory_context.

reason(insufficient_trusted_context) :- weak_context.
reason(single_source_context) :- single_source_context.
reason(contradictory_context) :- contradictory_context.
reason(context_consistency_unknown) :- context_consistency(unknown).

:- contradictory_context, selected_action(A), A != human_review.
1 { selected_action(A) : candidate_action(A) } 1.

action_cost(generate, 0).
action_cost(retrieve_again, 5).
action_cost(return_insufficient_context, 15).
action_cost(human_review, 10).
:~ selected_action(A), action_cost(A,C). [C@1,A]

selected_chunk(C) :- selected_action(generate), usable_chunk(C).

#show selected_action/1.
#show selected_chunk/1.
#show reason/1.
