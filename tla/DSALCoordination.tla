---- MODULE DSALCoordination ----
\* Bounded coordination model for the DSAL two-phase protocol.
\*
\* Scope (matches Section 5.3 of the manuscript):
\*   - models Request, Translate, Prepare, Commit, Respond and Abort;
\*   - models the interleaving of up to MaxReq concurrent cross-platform
\*     requests over Platforms, with one lock and one commit flag per
\*     (platform, request) pair;
\*   - does NOT model coordinator crash/failover, network partitions, lock
\*     expiry, or the Case (3) partial-commit window.
\*
\* Properties:
\*   NoPermissionLeakage   no request commits on any platform unless the
\*                         requesting organisation is permitted for its flow;
\*   SemanticConsistency   a translated or committed request carries a
\*                         platform policy that refines the abstract policy;
\*   Termination           every accepted request eventually reaches a
\*                         definitive response (responded or aborted), under
\*                         weak fairness on every action.

EXTENDS Naturals, TLC, FiniteSets

CONSTANTS Orgs, Platforms, Flows, MaxReq

\* Access table for the reported bounded configuration (Orgs = 1..3,
\* Flows = 1..2): organisation 3 may start either flow, organisation 1 only
\* flow 1, organisation 2 only flow 2.
Permitted(f, o) == (o = 3) \/ (f = 1 /\ o = 1) \/ (f = 2 /\ o = 2)

Req == 1..MaxReq
Statuses == {"idle", "requested", "translated", "preparing", "responded", "aborted"}

VARIABLES status, owner, flow, translated, locked, committed

vars == <<status, owner, flow, translated, locked, committed>>

\* Permitted[f][o] is TRUE when organisation o may start flow f.
\* AbstractPolicy[f] is the abstract access policy; translated[r] records the
\* platform policy produced by the translator, which must refine it.
AbstractPolicy(f) == {o \in Orgs : Permitted(f, o)}

Init ==
  /\ status     = [r \in Req |-> "idle"]
  /\ owner      = [r \in Req |-> CHOOSE o \in Orgs : TRUE]
  /\ flow       = [r \in Req |-> CHOOSE f \in Flows : TRUE]
  /\ translated = [r \in Req |-> {}]
  /\ locked     = [p \in Platforms |-> [r \in Req |-> FALSE]]
  /\ committed  = [p \in Platforms |-> [r \in Req |-> FALSE]]

\* ---------------------------------------------------------------- actions
Request(r) ==
  /\ status[r] = "idle"
  /\ \E o \in Orgs, f \in Flows :
       /\ owner' = [owner EXCEPT ![r] = o]
       /\ flow'  = [flow EXCEPT ![r] = f]
       /\ status' = [status EXCEPT ![r] = "requested"]
       /\ UNCHANGED <<translated, locked, committed>>

Translate(r) ==
  /\ status[r] = "requested"
  /\ \E pol \in SUBSET Orgs :
       \* the translator may only emit a policy that refines the abstract one
       /\ pol \subseteq AbstractPolicy(flow[r])
       /\ translated' = [translated EXCEPT ![r] = pol]
       /\ status' = [status EXCEPT ![r] = "translated"]
       /\ UNCHANGED <<owner, flow, locked, committed>>

Prepare(r, p) ==
  /\ status[r] \in {"translated", "preparing"}
  /\ ~locked[p][r]
  /\ owner[r] \in AbstractPolicy(flow[r])
  /\ locked' = [locked EXCEPT ![p][r] = TRUE]
  /\ status' = [status EXCEPT ![r] = "preparing"]
  /\ UNCHANGED <<owner, flow, translated, committed>>

Commit(r, p) ==
  /\ status[r] = "preparing"
  /\ \A q \in Platforms : locked[q][r]
  /\ locked[p][r]
  /\ ~committed[p][r]
  /\ committed' = [committed EXCEPT ![p][r] = TRUE]
  /\ UNCHANGED <<status, owner, flow, translated, locked>>

Respond(r) ==
  /\ status[r] = "preparing"
  /\ \A p \in Platforms : committed[p][r]
  /\ status' = [status EXCEPT ![r] = "responded"]
  /\ UNCHANGED <<owner, flow, translated, locked, committed>>

Abort(r) ==
  /\ status[r] \in {"requested", "translated"}
  /\ owner[r] \notin AbstractPolicy(flow[r])
  /\ status' = [status EXCEPT ![r] = "aborted"]
  /\ UNCHANGED <<owner, flow, translated, locked, committed>>

Next ==
  \/ \E r \in Req : Request(r) \/ Translate(r) \/ Respond(r) \/ Abort(r)
  \/ \E r \in Req, p \in Platforms : Prepare(r, p) \/ Commit(r, p)

Fairness ==
  \A r \in Req :
    /\ WF_vars(Request(r))
    /\ WF_vars(Translate(r))
    /\ WF_vars(Respond(r))
    /\ WF_vars(Abort(r))
    /\ \A p \in Platforms : WF_vars(Prepare(r, p)) /\ WF_vars(Commit(r, p))

Spec == Init /\ [][Next]_vars /\ Fairness

\* ------------------------------------------------------------- properties
NoPermissionLeakage ==
  \A r \in Req, p \in Platforms :
    committed[p][r] => owner[r] \in AbstractPolicy(flow[r])

SemanticConsistency ==
  \A r \in Req :
    status[r] \in {"translated", "preparing", "responded"} =>
      translated[r] \subseteq AbstractPolicy(flow[r])

Termination ==
  \A r \in Req :
    (status[r] # "idle") ~> (status[r] \in {"responded", "aborted"})

====
