% =====================================================================
% OUTPUT stage — allow, regenerate, return a grounded fallback, or block.
%
% Injected facts (built in facts.py):
%   judge(safe ; unsupported_answer ; out_of_domain_answer ; declined_no_context ;
%         system_prompt_leakage ; instruction_following_attack ; unknown).
%   confidence(0..100).  threshold(0..100).
%   context_chunks(0..N).
%   input_intent(...).   input_confidence(0..100).
%   generation_attempt(1..N).  max_generation_attempts(1..N).
% =====================================================================

security_violation(system_prompt_leakage) :- judge(system_prompt_leakage).
security_violation(instruction_following_attack) :- judge(instruction_following_attack).

judge_uncertain :- confidence(C), threshold(T), C < T.
unsupported :- judge(unsupported_answer).
out_of_domain :- judge(out_of_domain_answer).

% The generator answered "this is not in the official documents".  That is a
% refusal, and treating it as a normal answer made the control plane record
% `allow` with no reasons — a decline was indistinguishable from a success in
% the decision log.  It is NOT regenerated: the retry instruction pushes the
% model to stay closer to the context, so a second pass would decline again and
% cost another call for nothing.
declined :- judge(declined_no_context).

candidate_action(block) :- security_violation(_).
candidate_action(block) :- judge(unknown).
candidate_action(allow) :- judge(safe), not judge_uncertain.
candidate_action(regenerate) :- judge(safe), judge_uncertain,
                                generation_attempt(A), max_generation_attempts(M), A < M.
candidate_action(regenerate) :- unsupported, context_chunks(N), N > 0,
                                generation_attempt(A), max_generation_attempts(M), A < M.
candidate_action(return_insufficient_context) :- judge(safe), judge_uncertain,
                                                 generation_attempt(A), max_generation_attempts(M), A >= M.
candidate_action(return_insufficient_context) :- unsupported, context_chunks(N), N > 0,
                                                 generation_attempt(A), max_generation_attempts(M), A >= M.
candidate_action(return_insufficient_context) :- unsupported, context_chunks(0).
candidate_action(return_insufficient_context) :- out_of_domain.
candidate_action(return_insufficient_context) :- declined.

% ---- cross-stage coherence -------------------------------------------
% The input stage cleared the query as a confident in-scope question, yet the
% answer is off-domain.  By far the most likely cause is an intent-classifier
% false positive on a harmless off-topic question, NOT an attack: refuse
% cleanly and record the drift for offline classifier evaluation.  Routing this
% to human review made every mislabelled "how do I make pizza" a support ticket.
classifier_disagreement :- out_of_domain, input_intent(rag_query),
                           input_confidence(C), C >= 80.

% A *security* verdict on a query the input stage had cleared with high
% confidence is not explainable as a labelling error: both stages disagree on a
% safety-critical property.  The answer is blocked either way; the distinct
% reason is what makes the conflict auditable.
security_cross_stage_conflict :- security_violation(_), input_intent(rag_query),
                                 input_confidence(C), C >= 80.

consistent_out_of_domain :- out_of_domain, input_intent(out_of_scope).

reason(R) :- security_violation(R).
reason(unknown_output) :- judge(unknown).
reason(low_output_confidence) :- judge_uncertain.
reason(unsupported_answer) :- unsupported.
reason(out_of_domain_answer) :- out_of_domain.
reason(generator_declined_no_context) :- declined.
% The input stage was confident the corpus covers this, the generator found it
% does not.  Not a safety problem, but the pair is worth surfacing: it is the
% signal that the corpus has a gap the intent classifier does not know about.
reason(coverage_gap) :- declined, input_intent(rag_query), input_confidence(C), C >= 80.
reason(input_output_classifier_disagreement) :- classifier_disagreement.
reason(input_output_security_conflict) :- security_cross_stage_conflict.

:- security_violation(_), selected_action(A), A != block.

1 { selected_action(A) : candidate_action(A) } 1.

action_cost(allow, 0).
action_cost(regenerate, 5).
action_cost(return_insufficient_context, 10).
action_cost(block, 20).
:~ selected_action(A), action_cost(A,C). [C@1,A]

#show selected_action/1.
#show reason/1.
#show consistent_out_of_domain/0.
