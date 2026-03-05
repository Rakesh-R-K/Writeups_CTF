#!/usr/bin/env sage
# Sage script to attempt factoring / key recovery for the "Fractured RSA" challenge.
# Usage: run under Sage (e.g. `sage rsa_sage_solve.sage`).

from sage.all import *
import time

# Challenge parameters
n = Integer(647927383051035153094311600215454134185581785209016919095919486813598791877324408955728314346822866575767491833401044418159631987129380074016056700214054641032188888911569991709468242639422372153511769824703291707492725762824476715297654685162769998828070431607797733231564105232882552654444028400891784806220528971804251674816896058551093130355329257371410291247708502805063996497574099401821759172191433503389539026040820587860470706186411056087472417367108096246464902091593107093498583382490851935309009443324012387425807929834950952758635440098149888375068956874794565443546436486683128259096135709142760868727645750812165325404174747485870358006296019975599166459902660112352045868326593196856797732323301045507127237079316522403018789361236437406722556466258523628557404382229116925612927621980542155445909627456901107409622625997886306813021812135006759969044955582943898436768267493270431690788262122382940994959010995889165160731116227880092578561355772360409831279168444685885092597430763420519843660363183928777539782103358029669159423753382572433802237259958935316637228561440959471527406561815865353056268781899041176029047851669191813875783257779084043947323545744327582898190226883708623851808100418614901638992099879)
e = Integer(65537)
c = Integer(256768521843692080567823795051210485316412017278130999997404298981084930173094460233462767476579030746246692384982573250475264725711917533983943448747944692935954752589987794201734526904645844729996285146011303586022683922325411402808908690998966385120801411077580175324760916021331361169335958437993391889106097886294368617338082322776658659250044075924721728652999976331717938279126866570473088450005440039150868065580527862735320259590882550651565155611233086740290705990344519702217919552657131759936834865751217828036486843330335381628109730490903935562101526479534299660362233954971281532039503612812841732796660744865504543279651491108059829877715653141220810732573642078332170529562349252400171054366808021325132575387478716451319496496125537865082249156429088994847638054743776054756798961186478517876139520181147576055838704041757635109701304510433460170461682342578005378108437910330594838538605050721476589503336871609925709907326882858311933474886411419187083102176501340960676697942580947754531121356904087325120024185021518757336850370512155002867264516320479264778962248335975128155160153954068119985695422696223917700292390533434002090219940468763292146372667865220399275271803156622699931520696380255129642315165179)

# Optional: if you were given a leaked integer (e.g. low/high bits of p/q/d), set it here.
# Example: leak_val = Integer(<some integer>), leak_bits = <number_of_bits_known>
leak_val = None
leak_bits = None

def try_fermat(N, max_iters=5_000_000):
    """Fermat's factorization: good if p and q are close."""
    A = isqrt(N)
    if A*A < N:
        A += 1
    for i in range(max_iters):
        x = A*A - N
        if x >= 0:
            y = isqrt(x)
            if y*y == x:
                p = A - y
                q = A + y
                if p*q == N:
                    return Integer(p), Integer(q), i
        A += 1
        if i and i % 1000000 == 0:
            print('Fermat iter', i)
    return None


def pollard_brent(N, max_attempts=30):
    """Pollard-Brent implementation."""
    if N % 2 == 0:
        return Integer(2)
    for attempt in range(max_attempts):
        y = Integer(randint(1, N-1))
        c = Integer(randint(1, N-1))
        m = 100
        g = Integer(1)
        r = Integer(1)
        q = Integer(1)
        while g == 1:
            x = y
            for _ in range(int(r)):
                y = (y*y + c) % N
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, int(r-k))):
                    y = (y*y + c) % N
                    q = (q * abs(x-y)) % N
                g = gcd(q, N)
                k += m
            r *= 2
        if g == N:
            while True:
                ys = (ys*ys + c) % N
                g = gcd(abs(x-ys), N)
                if g > 1:
                    break
        if g != N and g != 1:
            return Integer(g)
    return None


def try_ecm(N, B1list=[1000,5000,20000,100000], timeout=30):
    """Attempt ECM using sage's ecm (if available)."""
    try:
        import sage.libs.ecm.ecm as _ecm
    except Exception:
        print('ECM library not available in this Sage environment')
        return None
    for B1 in B1list:
        print('ECM try B1=', B1)
        try:
            f = _ecm.factor(N, B1)
            if f and f[0] != N:
                return Integer(f[0])
        except Exception as ex:
            print('ECM exception', ex)
    return None


def coppersmith_high_bits(N, known_top, known_bits, X=None, beta=0.5):
    """
    Try Coppersmith when the most-significant `known_bits` of p are known.
    `known_top` should be the integer formed by those top bits (i.e. p = known_top << (p_bits-known_bits) + x).
    This routine constructs polynomials and uses Sage's small_roots routine.
    Note: run under Sage (polynomial.small_roots).
    """
    print('Attempting Coppersmith high-bits. known_bits=', known_bits)
    P = PolynomialRing(Zmod(N), 'x')
    x = P.gen()
    # Let p = known_top * 2^shift + x
    p_bits = N.nbits() // 2
    shift = p_bits - known_bits
    a = Integer(known_top) * (2**shift)
    f = x + Integer(a)
    if X is None:
        # bound on x
        X = 2**(shift)
    try:
        roots = f.small_roots(X=X, beta=beta)
        if roots:
            for r in roots:
                p = Integer(a) + Integer(r)
                if p > 1 and N % p == 0:
                    return p
    except Exception as ex:
        print('small_roots failed:', ex)
    return None


def coppersmith_low_bits(N, known_low, known_bits, X=None, beta=0.5):
    """
    Try Coppersmith when the least-significant `known_bits` of p are known.
    p = known_low + 2^known_bits * x
    """
    print('Attempting Coppersmith low-bits. known_bits=', known_bits)
    P = PolynomialRing(Zmod(N), 'x')
    x = P.gen()
    f = Integer(known_low) + (Integer(2)**Integer(known_bits)) * x
    if X is None:
        X = 2**(N.nbits()//2 - known_bits)
    try:
        roots = f.small_roots(X=X, beta=beta)
        if roots:
            for r in roots:
                p = Integer(known_low) + (Integer(2)**Integer(known_bits))*Integer(r)
                if p > 1 and N % p == 0:
                    return p
    except Exception as ex:
        print('small_roots failed:', ex)
    return None


def main():
    print('n bit-length:', n.nbits())
    t0 = time.time()

    # 1) Fermat
    print('\n[1] Trying Fermat')
    res = try_fermat(n, max_iters=5_000_000)
    if res:
        p, q, it = res
        print('Fermat success: p bits', p.nbits(), 'q bits', q.nbits())
        print('p=', p)
        print('q=', q)
    else:
        print('Fermat failed within limit')

    # 2) Pollard-Brent
    found = False
    if not res:
        print('\n[2] Trying Pollard-Brent')
        f = pollard_brent(n, max_attempts=40)
        if f:
            p = Integer(f); q = n//p
            print('Pollard-Brent found factor')
            print('p bits', p.nbits())
            found = True
        else:
            print('Pollard-Brent failed')

    # 3) ECM
    if not res and not found:
        print('\n[3] Trying ECM (if available)')
        f_ecm = try_ecm(n)
        if f_ecm:
            p = Integer(f_ecm); q = n//p
            print('ECM found factor')
            found = True
        else:
            print('ECM found nothing (or not available)')

    # 4) Coppersmith attempts if leak provided
    if leak_val is not None and leak_bits is not None:
        print('\n[4] Trying Coppersmith with provided leak')
        # try treating leak as high bits
        p0 = coppersmith_high_bits(n, leak_val, leak_bits)
        if p0:
            print('Coppersmith (high) found p=', p0)
            p = p0; q = n//p
            found = True
        else:
            p0 = coppersmith_low_bits(n, leak_val, leak_bits)
            if p0:
                print('Coppersmith (low) found p=', p0)
                p = p0; q = n//p
                found = True
            else:
                print('Coppersmith attempts failed')

    # If we have p and q, compute d and decrypt
    if 'p' in globals() and p and n % p == 0:
        q = n // p
        phi = (p-1)*(q-1)
        d = inverse_mod(e, phi)
        m = power_mod(c, d, n)
        pt = Integer(m).to_bytes((m.nbits()+7)//8, byteorder='big')
        print('\nDecrypted plaintext bytes:', pt)
        try:
            print('Plaintext:', pt.decode())
        except Exception:
            print('Plaintext (repr):', repr(pt))

    print('\nElapsed time:', time.time()-t0)


if __name__ == '__main__':
    main()
