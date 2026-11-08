#!/usr/bin/env python3
"""DSAL-Egov Concept Benchmark v1 -- synthetic generator.

The benchmark is a *controlled synthetic* concept-mapping corpus for the
cross-agency e-government setting evaluated in the manuscript.  It encodes 24
abstract DSAL concepts and their documented realisations on Hyperledger Fabric,
FISCO BCOS and Corda.  Gold labels are exact by construction: every pair is
generated from a concept identity, so no human annotation is involved and no
third-party material is used.

Task formulation (candidate ranking).  For every (source description, target
platform) pair the model must rank the 24 platform concepts of that platform
and place the correct concept first.

Outputs
-------
egov_concept_pairs.csv   one row per (pair_id, source, target platform, gold)
concept_vocabulary.csv   the 24 concepts with their three platform terms
benchmark_stats.json     size / split / difficulty statistics

Usage:  python3 generate_benchmark.py [--out .] [--variants 75] [--seed 20261105]
License: CC BY 4.0 (data), MIT (code).
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

# --------------------------------------------------------------------------
# Concept table
# --------------------------------------------------------------------------
# Each entry: family, DSAL term, DSAL gloss variants, and the three platform
# realisations (term + two documentation-style glosses each).
CONCEPTS = [
    dict(
        id="C01", family="isolation", term="Isolation Domain",
        dsal=["a logical partition that isolates transaction visibility for a defined set of organisations",
              "a scoped ledger environment shared only by the agencies that take part in a workflow"],
        fabric=("Channel", [
            "a private ledger partition shared by a subset of member organisations",
            "an isolated sub-network whose ledger and chaincode are visible only to its members"]),
        bcos=("Group", [
            "an independent ledger group with its own consensus and storage",
            "a separately maintained ledger that keeps its data apart from other groups"]),
        corda=("Business Network", [
            "a governed set of nodes that share states under a common set of rules",
            "a permissioned network whose participants exchange states privately"]),
    ),
    dict(
        id="C02", family="isolation", term="Membership Set",
        dsal=["the organisations that are entitled to read and write inside one partition",
              "the enumerated agencies admitted to a shared ledger environment"],
        fabric=("Channel Membership", [
            "the consortium members whose certificates are recognised on a channel",
            "the set of organisations configured into a channel's consortium"]),
        bcos=("Group Member List", [
            "the agencies registered as members of one group",
            "the node list that is authorised to join a group"]),
        corda=("Network Participants", [
            "the parties that hold identities on a Corda network",
            "the organisations admitted to a shared Corda network"]),
    ),
    dict(
        id="C03", family="isolation", term="Private Data Scope",
        dsal=["the subset of records that must stay hidden from other participants in the same partition",
              "a confidentiality boundary applied to selected fields of a shared record"],
        fabric=("Private Data Collection", [
            "a side database that shares selected key values with named organisations only",
            "a collection policy that keeps transaction payloads off the public channel ledger"]),
        bcos=("Group Storage Isolation", [
            "separate storage that keeps one group's records away from other groups",
            "per-group data storage with its own access boundary"]),
        corda=("Confidential State", [
            "a state that is distributed only to the parties named in the transaction",
            "need-to-know distribution of ledger states to a subset of counterparties"]),
    ),
    dict(
        id="C04", family="identity", term="Organisation Identity",
        dsal=["the verifiable digital identity of an agency or enterprise that acts on the ledger",
              "the credential that establishes which legal entity is transacting"],
        fabric=("Membership Service Provider", [
            "the component that issues and validates the certificates that define an organisation",
            "a membership definition that binds an organisation to its root certificate and peers"]),
        bcos=("Agency Account", [
            "the on-chain account that represents a participating institution",
            "the registered institutional account used to submit transactions"]),
        corda=("Organisation Identity", [
            "the certificate-backed identity of a legal entity on the network",
            "the party identity that represents one organisation"]),
    ),
    dict(
        id="C05", family="identity", term="Certificate Authority",
        dsal=["the service that issues and revokes the certificates used to authenticate participants",
              "the trust anchor that signs enrolment credentials for agencies"],
        fabric=("Fabric CA", [
            "the certificate authority that enrols identities and issues enrolment certificates",
            "the PKI service that registers and revokes member credentials"]),
        bcos=("CA Node", [
            "the certificate node that issues institution certificates for the chain",
            "the authority node responsible for issuing and revoking agency certificates"]),
        corda=("Identity Manager", [
            "the service that issues and manages participant identity certificates",
            "the network service that signs and tracks party certificates"]),
    ),
    dict(
        id="C06", family="identity", term="Role Binding",
        dsal=["the assignment of an authorised role to an identity for a defined resource",
              "the mapping between an organisational role and the actions it may perform"],
        fabric=("Attribute-Based Access", [
            "attributes embedded in an identity certificate that gate chaincode functions",
            "certificate attributes used to decide which operations an identity may invoke"]),
        bcos=("Role Table", [
            "a table that binds roles to permitted contract methods",
            "the role registry consulted before a contract call is executed"]),
        corda=("Party Role", [
            "a role attribute attached to a party that constrains flow participation",
            "the role assignment that determines which flows a party may start"]),
    ),
    dict(
        id="C07", family="consensus", term="Ordering Service",
        dsal=["the component that establishes a single order for transactions before they are committed",
              "the sequencing function that places transactions into an agreed order"],
        fabric=("Orderer", [
            "the node that orders transactions and assembles them into blocks",
            "the ordering node that delivers ordered blocks to committing peers"]),
        bcos=("Consensus Node", [
            "the node that reaches agreement on block order under PBFT",
            "a validating node that participates in the consensus round"]),
        corda=("Notary", [
            "the service that prevents double spending by signing unique input states",
            "the uniqueness service that attests a transaction's inputs are unconsumed"]),
    ),
    dict(
        id="C08", family="consensus", term="Finality Point",
        dsal=["the moment after which a committed record is treated as irreversible",
              "the point at which a transaction can no longer be reordered or rolled back"],
        fabric=("Block Commit", [
            "the point at which a block is validated and written to the peer ledger",
            "block validation and persistence on the committing peer"]),
        bcos=("PBFT Commit", [
            "the phase in which a block is finalised by a supermajority of consensus nodes",
            "the commit phase that makes a block irreversible under PBFT"]),
        corda=("Notarised Transaction", [
            "a transaction whose inputs have been signed off by the notary",
            "the state of a transaction once notarisation has completed"]),
    ),
    dict(
        id="C09", family="consensus", term="Block Proposal",
        dsal=["the batch of ordered transactions that is offered for validation",
              "a candidate batch of records awaiting commitment"],
        fabric=("Block", [
            "an ordered batch of transactions delivered to peers for validation",
            "the unit of ordering that carries a set of endorsed transactions"]),
        bcos=("Block", [
            "a sealed batch of transactions produced by the consensus round",
            "the consensus output that groups transactions for execution"]),
        corda=("Transaction", [
            "an atomic proposal that consumes input states and produces output states",
            "the unit of ledger update that is signed by the involved parties"]),
    ),
    dict(
        id="C10", family="contract", term="Contract Package",
        dsal=["the deployable unit of business logic together with its dependencies",
              "the packaged code artefact that is installed on a ledger"],
        fabric=("Chaincode", [
            "a program installed and instantiated on a channel to implement business logic",
            "the smart contract package executed in an isolated container"]),
        bcos=("Solidity Contract", [
            "a contract compiled to bytecode and deployed to a group",
            "the EVM contract artefact that implements on-chain logic"]),
        corda=("CorDapp", [
            "a distributed application packaged as a set of contracts and flows",
            "the deployable application bundle that defines contracts and flows"]),
    ),
    dict(
        id="C11", family="contract", term="Contract Lifecycle",
        dsal=["the sequence of install, approve, commit and instantiate operations for a contract",
              "the staged process by which contract code becomes active on a ledger"],
        fabric=("Chaincode Lifecycle", [
            "the install, approve, commit sequence defined by the Fabric lifecycle",
            "the packaging and approval workflow that activates chaincode on a channel"]),
        bcos=("Contract Deployment", [
            "the transaction that publishes contract bytecode to a group",
            "the deployment step that makes a contract callable"]),
        corda=("Contract Attachment", [
            "the process of attaching contract code to a transaction for verification",
            "the mechanism that binds a contract version to a transaction"]),
    ),
    dict(
        id="C12", family="contract", term="Contract Upgrade",
        dsal=["the controlled replacement of active business logic while preserving stored state",
              "the governed migration of a deployed contract to a new version"],
        fabric=("Chaincode Upgrade", [
            "re-instantiation of a chaincode definition at a higher version",
            "the lifecycle operation that replaces chaincode code without dropping state"]),
        bcos=("Contract Upgrade", [
            "the administrative transaction that points a contract address at new bytecode",
            "the migration of a deployed contract to a revised implementation"]),
        corda=("Contract Constraint Upgrade", [
            "the replacement of a contract constraint by a ratified new version",
            "the governed change of the contract rules attached to a state"]),
    ),
    dict(
        id="C13", family="policy", term="Endorsement Policy",
        dsal=["the rule that states which parties must approve a transaction before it is accepted",
              "the approval requirement attached to a state-changing operation"],
        fabric=("Endorsement Policy", [
            "the policy that specifies which organisations must endorse a proposal",
            "the signature policy evaluated before a transaction is committed"]),
        bcos=("Permission Contract", [
            "the precompiled contract that checks whether a caller holds the required permission",
            "the on-chain rule that validates caller authority before execution"]),
        corda=("Contract Constraint", [
            "the constraint that determines which contract code must verify a transaction",
            "the rule attached to a state that restricts how it may be updated"]),
    ),
    dict(
        id="C14", family="policy", term="Access Rule",
        dsal=["the rule that permits or denies a specific action on a named resource",
              "the resource-action permission checked at invocation time"],
        fabric=("Access Control List", [
            "the list that maps channel resources to the identities allowed to use them",
            "the ACL entry that gates an administrative or chaincode operation"]),
        bcos=("Permission Table", [
            "the table that records which accounts may call which contract methods",
            "the permission registry consulted for each external call"]),
        corda=("Flow Permission", [
            "the permission that determines whether a party may initiate a flow",
            "the authorisation check applied when a flow is started"]),
    ),
    dict(
        id="C15", family="policy", term="Approval Threshold",
        dsal=["the minimum number of distinct approvers required for an operation to succeed",
              "the quorum size that a multi-party approval must reach"],
        fabric=("M-of-N Endorsement", [
            "a policy requiring m of n listed organisations to endorse",
            "the threshold signature policy over a named organisation set"]),
        bcos=("Multi-signature Rule", [
            "a rule that requires several account signatures before execution",
            "the weighted multi-signature condition enforced by the permission contract"]),
        corda=("Required Signers", [
            "the signer set that a transaction must carry to satisfy its contract",
            "the mandatory signing parties encoded in the contract constraint"]),
    ),
    dict(
        id="C16", family="workflow", term="Business Flow",
        dsal=["a declarative template that expresses a multi-step administrative process",
              "the directed graph of business steps, roles and execution constraints"],
        fabric=("Invocation Sequence", [
            "the ordered sequence of chaincode invocations that implements a process",
            "the client-driven series of endorsed invocations forming a workflow"]),
        bcos=("Transaction Sequence", [
            "the ordered set of contract calls that advances a business process",
            "the chained transactions that implement a multi-step procedure"]),
        corda=("Flow", [
            "a program that coordinates the steps of a multi-party business process",
            "the orchestration routine that exchanges messages between counterparties"]),
    ),
    dict(
        id="C17", family="workflow", term="Approval Step",
        dsal=["a single stage in a process at which one role must approve before the process continues",
              "an intermediate checkpoint that requires an authorised decision"],
        fabric=("Endorsement Round", [
            "one collection round in which peers simulate and endorse a proposal",
            "the endorsement exchange that completes a single approval stage"]),
        bcos=("Approval Transaction", [
            "the transaction that records one agency's approval decision",
            "the contract call that advances an approval counter"]),
        corda=("SubFlow", [
            "a nested flow that performs one stage of a larger process",
            "a reusable flow fragment invoked at one approval stage"]),
    ),
    dict(
        id="C18", family="workflow", term="Compensation Action",
        dsal=["the corrective operation that offsets an earlier step which can no longer be rolled back",
              "the remedial transaction used when a completed step must be undone logically"],
        fabric=("Reverse Transaction", [
            "a compensating invocation that restores a previously committed key value",
            "the offsetting chaincode call used after an irreversible commit"]),
        bcos=("Rollback Transaction", [
            "a contract call that writes back the prior state after a partial failure",
            "the compensating transaction issued when a peer step fails"]),
        corda=("Compensation", [
            "a flow that issues offsetting states for an already consumed state",
            "the remedial flow used when a completed exchange must be reversed"]),
    ),
    dict(
        id="C19", family="workflow", term="Timeout Handler",
        dsal=["the policy that decides what happens when a step does not complete within its deadline",
              "the expiry rule applied to an in-flight operation"],
        fabric=("Endorsement Timeout", [
            "the client-side deadline after which an endorsement request is abandoned",
            "the time limit applied to collecting proposal responses"]),
        bcos=("Transaction Expiry", [
            "the block-height or time bound after which a transaction is rejected",
            "the validity window attached to a submitted transaction"]),
        corda=("Flow Timeout", [
            "the deadline after which a suspended flow is aborted",
            "the timer that terminates a waiting flow"]),
    ),
    dict(
        id="C20", family="audit", term="Audit Record",
        dsal=["the durable record of who did what and when, retained for oversight",
              "the evidential entry that supports later inspection of an action"],
        fabric=("Transaction Log", [
            "the ledger record of validated transactions retained by each peer",
            "the append-only transaction history held on the channel"]),
        bcos=("Block Receipt", [
            "the receipt that records a transaction's status and block position",
            "the stored execution result referenced by block height"]),
        corda=("Vault Audit", [
            "the recorded history of state consumption and production in the vault",
            "the audit trail of transactions affecting a party's states"]),
    ),
    dict(
        id="C21", family="audit", term="Operation Credential",
        dsal=["the consolidated evidence that a cross-platform operation completed as requested",
              "the signed proof combining receipts from every participating ledger"],
        fabric=("Signed Proposal Response", [
            "the endorsed response signed by each endorsing peer",
            "the proposal response carrying endorsement signatures"]),
        bcos=("Transaction Receipt", [
            "the signed receipt returned after a contract call is mined",
            "the execution receipt proving a transaction was included"]),
        corda=("Signed Transaction", [
            "the notarised transaction carrying all required signatures",
            "the finalised transaction with counterparty and notary signatures"]),
    ),
    dict(
        id="C22", family="audit", term="Event Subscription",
        dsal=["the registration that delivers notifications when a named ledger event occurs",
              "the listener that receives emitted business events"],
        fabric=("Chaincode Event", [
            "an event emitted by chaincode and delivered to registered listeners",
            "the channel event that a client subscribes to"]),
        bcos=("Event Log", [
            "the log topic that clients watch for contract-emitted events",
            "the emitted log entry consumed by an off-chain subscriber"]),
        corda=("Observer", [
            "a node that receives updates for states it is not a participant of",
            "the observer subscription that forwards transaction updates"]),
    ),
    dict(
        id="C23", family="data", term="World State",
        dsal=["the current value of all committed business objects",
              "the latest committed view of ledger state used for queries"],
        fabric=("State Database", [
            "the key-value database that holds the latest world state for a channel",
            "the peer-side state store queried by chaincode"]),
        bcos=("State Trie", [
            "the Merkle Patricia trie that stores current account and contract state",
            "the trie structure holding the latest committed state root"]),
        corda=("Vault", [
            "the local database that stores the states a party is aware of",
            "the per-node store of current and historic states"]),
    ),
    dict(
        id="C24", family="data", term="Historical Query",
        dsal=["the retrieval of earlier versions of a record for dispute resolution",
              "the point-in-time read of how a business object changed"],
        fabric=("History Database", [
            "the index that returns the modification history of a key",
            "the query interface that replays key updates over time"]),
        bcos=("Archive Node Query", [
            "a query served by an archive node over historic blocks",
            "the historic block lookup performed against archived data"]),
        corda=("Vault Query", [
            "a query over recorded states including consumed ones",
            "the vault query language used to retrieve historic states"]),
    ),
]

PLATFORMS = ["fabric", "bcos", "corda"]
PLATFORM_NAME = {"fabric": "Hyperledger Fabric", "bcos": "FISCO BCOS", "corda": "Corda"}

# Documentation-style wrappers.  They add surface variation without changing
# the semantics, mimicking the phrasing differences between vendor documents.
WRAPPERS = [
    "{c}.",
    "In {p} documentation, {c}.",
    "The {p} construct described as {c}.",
    "Operationally, {c}.",
    "At run time, {c}.",
    "{c} (as documented for {p}).",
    "For {p}, {c}.",
    "The platform documentation refers to {c} as follows.",
]

QUALIFIERS = [
    "",
    " This is configured per {unit}.",
    " It is managed by the platform administrator.",
    " The setting is recorded in the ledger configuration.",
    " It applies to every node in the deployment.",
    " The value is read when a transaction is submitted.",
    " Operators can inspect it through the administrative interface.",
    " The behaviour is unchanged across releases.",
]

UNIT = {"fabric": "channel", "bcos": "group", "corda": "network"}


def build_variants(concept: dict, platform: str, n: int, rng: random.Random):
    """Sample n *distinct* surface variants for one (concept, platform) cell.

    The variant space is the full cartesian product of the documented glosses,
    the wrapper templates and the qualifier templates, so the same description
    can never be generated twice.  Sampling is without replacement; if a cell
    had fewer than n distinct combinations the call fails loudly rather than
    silently duplicating text.
    """
    term, glosses = concept[platform]
    space = []
    for g in glosses:
        for w in WRAPPERS:
            head = w.format(c=g, p=PLATFORM_NAME[platform])
            for q in QUALIFIERS:
                space.append(head + q.format(unit=UNIT[platform]))
    if len(space) < n:
        raise ValueError(
            f"cell {concept['id']}/{platform} has only {len(space)} distinct "
            f"variants but {n} were requested")
    return rng.sample(space, n)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--variants", type=int, default=75,
                    help="source-description variants per (concept, platform)")
    ap.add_argument("--seed", type=int, default=20261105)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    pid = 0
    per_concept = defaultdict(int)
    for concept in CONCEPTS:
        for platform in PLATFORMS:
            term = concept[platform][0]
            for desc in build_variants(concept, platform, args.variants, rng):
                pid += 1
                rows.append(dict(
                    pair_id=f"P{pid:05d}",
                    concept_id=concept["id"],
                    family=concept["family"],
                    dsal_term=concept["term"],
                    target_platform=platform,
                    gold_term=term,
                    source_description=desc,
                ))
                per_concept[concept["id"]] += 1

    rng.shuffle(rows)
    # Stratified 70/15/15 split by (concept, platform) so that every concept is
    # represented in every split and no surface variant leaks across splits.
    buckets = defaultdict(list)
    for r in rows:
        buckets[(r["concept_id"], r["target_platform"])].append(r)
    for key in buckets:
        rng.shuffle(buckets[key])
    for key, items in buckets.items():
        n = len(items)
        n_tr = int(round(0.70 * n))
        n_va = int(round(0.15 * n))
        for i, r in enumerate(items):
            r["split"] = "train" if i < n_tr else ("val" if i < n_tr + n_va else "test")

    rows.sort(key=lambda r: r["pair_id"])
    fields = ["pair_id", "concept_id", "family", "dsal_term", "target_platform",
              "gold_term", "source_description", "split"]
    with (outdir / "egov_concept_pairs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    with (outdir / "concept_vocabulary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["concept_id", "family", "dsal_term", "platform", "platform_term",
                    "documented_gloss"])
        for c in CONCEPTS:
            for p in PLATFORMS:
                w.writerow([c["id"], c["family"], c["term"], p, c[p][0], c[p][1][0]])

    split_counts = Counter(r["split"] for r in rows)

    # --- integrity checks: no duplicate descriptions, no train/test overlap ---
    norm = lambda t: " ".join(t.strip().lower().split())
    distinct = {norm(r["source_description"]) for r in rows}
    assert len(distinct) == len(rows), (
        f"duplicate descriptions: {len(rows) - len(distinct)} rows collide")
    train_text = {norm(r["source_description"]) for r in rows if r["split"] != "test"}
    test_text = {norm(r["source_description"]) for r in rows if r["split"] == "test"}
    overlap = train_text & test_text
    assert not overlap, f"{len(overlap)} test descriptions also occur in train/val"
    stats = dict(
        version="1.0",
        generated_with="generate_benchmark.py",
        seed=args.seed,
        seed_concept_count=len(CONCEPTS),
        platforms={p: PLATFORM_NAME[p] for p in PLATFORMS},
        pairs=len(rows),
        variants_per_concept_platform=args.variants,
        families=dict(Counter(c["family"] for c in CONCEPTS)),
        split_counts=dict(split_counts),
        candidate_pool_size=len(CONCEPTS),
        distinct_descriptions=len(distinct),
        test_train_overlap=len(overlap),
        note=("Fully synthetic: every description is produced from the embedded "
              "concept table by the released script, sampled without replacement "
              "so that no two pairs share a description and no test description "
              "occurs in training. Gold labels are exact by construction. The "
              "corpus contains no material from any employer, agency or third party."),
    )
    (outdir / "benchmark_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
