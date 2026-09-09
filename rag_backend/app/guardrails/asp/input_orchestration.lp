% =====================================================================
% INPUT stage — multi-action orchestration.
%
% Injected facts (built in facts.py):
%   signal_llm_guard(safe ; unsafe).
%   signal_intent_classifier(executed ; skipped).
%   intent(rag_query ; general_chat ; prompt_injection ;
%          system_info_request ; out_of_scope ; unknown).
%   confidence(0..100).            % classifier confidence, rescaled
%   threshold(0..100).             % min confidence to auto-trust a RAG_QUERY
%   authenticated(true ; false).
%   user_role(anonymous ; user ; admin).
%   recent_security_events(0..N).  % security-relevant blocks in the last 24h
%   privileged_debug_request.      % optional
%
% Derived:
%   selected_action(retrieve ; ask_clarification ; allow_general_chat ;
%                   allow_privileged_debug ; human_review ; block).
% =====================================================================

% ---- hard security violations ---------------------------------------
hard_violation(llm_guard) :- signal_llm_guard(unsafe).
hard_violation(prompt_injection) :- intent(prompt_injection).

privileged_debug :- privileged_debug_request,
                    authenticated(true), user_role(admin).
hard_violation(system_info_request) :- intent(system_info_request), not privileged_debug.

% ---- machine-undecidable situations ---------------------------------
% The two security classifiers contradict each other: neither label can be
% trusted, so the request genuinely needs a human.
conflict(security_classifiers) :- signal_llm_guard(safe),
                                  intent(prompt_injection), confidence(C), C >= 80.

% The request itself carries no security signal, but the system cannot tell
% what the user is asking for.
ambiguous_request :- intent(rag_query), confidence(C), threshold(T), C < T.
ambiguous_request :- intent(unknown), signal_intent_classifier(executed).

% ---- account-level risk ---------------------------------------------
% Repeated *security-relevant* blocks raise scrutiny on this account.
% Privileged accounts escalate earlier because compromise has greater impact.
elevated_recent_risk :- user_role(user), recent_security_events(N), N >= 3.
elevated_recent_risk :- user_role(admin), recent_security_events(N), N >= 2.

% Elevated risk is a *modifier*, not an override.  It upgrades an ambiguous
% request to human review, because that is the band where a human adds
% information.  It deliberately does NOT touch requests the policy can already
% decide on its own: a clean in-scope question is still answered, a clearly
% out-of-scope question is still refused, and a hard violation is still handled
% by the rules below.  Making this an unconditional constraint was what turned
% every subsequent query from a flagged account — including a harmless
% off-topic one — into a human-review ticket.
escalate_to_human :- elevated_recent_risk, ambiguous_request.
escalate_to_human :- conflict(_), authenticated(true).

% ---- candidate actions ----------------------------------------------
candidate_action(block) :- hard_violation(_).
candidate_action(human_review) :- escalate_to_human.
candidate_action(retrieve) :- intent(rag_query), confidence(C), threshold(T), C >= T,
                              not hard_violation(_).
candidate_action(ask_clarification) :- intent(rag_query), confidence(C), threshold(T), C < T,
                                       not hard_violation(_).
candidate_action(allow_general_chat) :- intent(general_chat), not hard_violation(_).
candidate_action(allow_privileged_debug) :- intent(system_info_request), privileged_debug,
                                             not hard_violation(_).
candidate_action(block) :- intent(out_of_scope).
candidate_action(block) :- intent(unknown), signal_intent_classifier(executed).
% A skipped classifier is expected after an earlier hard gate.  It is a
% configuration failure only when the earlier gate considered the input safe.
candidate_action(block) :- signal_intent_classifier(skipped), signal_llm_guard(safe).

% ---- explanations ----------------------------------------------------
reason(R) :- hard_violation(R).
reason(security_classifier_conflict) :- conflict(security_classifiers).
% Recorded even when it does not change the action, so the escalation state of
% an account stays visible in the decision log.
reason(repeated_recent_security_events) :- elevated_recent_risk.
reason(privileged_admin_debug) :- intent(system_info_request), privileged_debug.
reason(low_intent_confidence) :- intent(rag_query), confidence(C), threshold(T), C < T.
reason(out_of_scope) :- intent(out_of_scope).
reason(unknown_intent) :- intent(unknown), signal_intent_classifier(executed).
reason(intent_classifier_not_run) :- signal_intent_classifier(skipped), signal_llm_guard(safe).

% ---- integrity constraints -------------------------------------------
% Hard violations cannot be bypassed by an optimized softer action.  human_review
% stays admissible because a classifier conflict is itself a hard violation
% (intent=prompt_injection) that a human must adjudicate.
:- hard_violation(_), selected_action(A), A != block, A != human_review.
:- escalate_to_human, selected_action(A), A != human_review.

1 { selected_action(A) : candidate_action(A) } 1.

action_cost(block, 30).
action_cost(human_review, 20).
action_cost(ask_clarification, 10).
action_cost(retrieve, 0).
action_cost(allow_general_chat, 0).
action_cost(allow_privileged_debug, 0).
:~ selected_action(A), action_cost(A,C). [C@1,A]

#show selected_action/1.
#show reason/1.
