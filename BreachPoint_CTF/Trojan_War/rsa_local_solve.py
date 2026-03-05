#!/usr/bin/env python3
"""Local RSA solver: Fermat, Pollard-Brent, pyecm attempts, then decrypt c if factored."""
import math
import random
import sys
import time

try:
    import pyecm
except Exception:
    pyecm = None

# Parameters (from challenge)
n = 647927383051035153094311600215454134185581785209016919095919486813598791877324408955728314346822866575767491833401044418159631987129380074016056700214054641032188888911569991709468242639422372153511769824703291707492725762824476715297654685162769998828070431607797733231564105232882552654444028400891784806220528971804251674816896058551093130355329257371410291247708502805063996497574099401821759172191433503389539026040820587860470706186411056087472417367108096246464902091593107093498583382490851935309009443324012387425807929834950952758635440098149888375068956874794565443546436486683128259096135709142760868727645750812165325404174747485870358006296019975599166459902660112352045868326593196856797732323301045507127237079316522403018789361236437406722556466258523628557404382229116925612927621980542155445909627456901107409622625997886306813021812135006759969044955582943898436768267493270431690788262122382940994959010995889165160731116227880092578561355772360409831279168444685885092597430763420519843660363183928777539782103358029669159423753382572433802237259958935316637228561440959471527406561815865353056268781899041176029047851669191813875783257779084043947323545744327582898190226883708623851808100418614901638992099879
e = 65537
c = 256768521843692080567823795051210485316412017278130999997404298981084930173094460233462767476579030746246692384982573250475264725711917533983943448747944692935954752589987794201734526904645844729996285146011303586022683922325411402808908690998966385120801411077580175324760916021331361169335958437993391889106097886294368617338082322776658659250044075924721728652999976331717938279126866570473088450005440039150868065580527862735320259590882550651565155611233086740290705990344519702217919552657131759936834865751217828036486843330335381628109730490903935562101526479534299660362233954971281532039503612812841732796660744865504543279651491108059829877715653141220810732573642078332170529562349252400171054366808021325132575387478716451319496496125537865082249156429088994847638054743776054756798961186478517876139520181147576055838704041757635109701304510433460170461682342578005378108437910330594838538605050721476589503336871609925709907326882858311933474886411419187083102176501340960676697942580947754531121356904087325120024185021518757336850370512155002867264516320479264778962248335975128155160153954068119985695422696223917700292390533434002090219940468763292146372667865220399275271803156622699931520696380255129642315165179


def is_perfect_square(n):
    if n < 0:
        return False
    t = math.isqrt(n)
    return t*t == n


def fermat_factor(n, max_iters=5_000_000):
    A = math.isqrt(n)
    if A*A < n:
        A += 1
    for i in range(max_iters):
        x = A*A - n
        if x >= 0:
            y = math.isqrt(x)
            if y*y == x:
                p = A - y
                q = A + y
                if p > 1 and q > 1 and p*q == n:
                    return p, q, i
        A += 1
        if i and i % 1000000 == 0:
            print(f'Fermat: {i} iterations')
    return None


def pollard_brent(n, max_attempts=20):
    if n % 2 == 0:
        return 2
    for attempt in range(max_attempts):
        y = random.randrange(1, n-1)
        c = random.randrange(1, n-1)
        m = 100
        g = 1
        r = 1
        q = 1
        x = y
        ys = y
        while g == 1:
            x = y
            for _ in range(r):
                y = (y*y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r-k)):
                    y = (y*y + c) % n
                    q = q * abs(x-y) % n
                g = math.gcd(q, n)
                k += m
            r *= 2
        if g == n:
            # retry inner loop
            g = 1
            while g == 1:
                ys = (ys*ys + c) % n
                g = math.gcd(abs(x-ys), n)
        if g != n and g != 1:
            return g
    return None


def try_ecm(n, bounds=[1000,5000,20000,100000], timeout=30):
    if not pyecm:
        print('pyecm not available')
        return None
    for B1 in bounds:
        print('ECM attempt B1=', B1)
        try:
            for f in pyecm.factors(n, False, B1=B1, timeout=timeout, verbose=False):
                if 1 < f < n:
                    return f
        except Exception as e:
            print('ECM error', e)
    return None


def invmod(a, m):
    return pow(a, -1, m)


def try_all():
    start = time.time()
    print('n bitlen', n.bit_length())

    print('Trying Fermat (fast)')
    res = fermat_factor(n, max_iters=2_000_000)
    if res:
        p, q, iters = res
        print('Fermat found p,q in', iters, 'iters')
    else:
        print('Fermat did not find factors within limit')

    if not res:
        print('Trying Pollard-Brent')
        f = pollard_brent(n, max_attempts=40)
        if f:
            p = f
            q = n//p
            print('Pollard-Brent found factor')
        else:
            print('Pollard-Brent failed; trying ECM')
            f = try_ecm(n, bounds=[1000,5000,20000,100000,500000], timeout=20)
            if f:
                p = f
                q = n//p
                print('ECM found factor')
            else:
                print('No factor found by Pollard/ECM')
                return

    # Ensure p<q
    if p > n//p:
        p, q = q, p

    print('p bits', p.bit_length(), 'q bits', q.bit_length())
    print('p=', p)
    print('q=', q)

    phi = (p-1)*(q-1)
    d = invmod(e, phi)
    print('Computed d (bitlen):', d.bit_length())
    m = pow(c, d, n)
    bt = m.to_bytes((m.bit_length()+7)//8, 'big')
    print('Decrypted bytes:', bt)
    try:
        print('Plaintext:', bt.decode())
    except Exception:
        print('Plaintext (repr):', repr(bt))

    print('Elapsed', time.time()-start)


if __name__ == '__main__':
    try:
        try_all()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(1)
