# Challenge: Fractured RSA

## Challenge Description
The challenge provides two RSA ciphertexts ($c_1$, $c_2$) encrypted using the same modulus ($n$) and public exponent ($e = 65537$). A crucial hint is provided: the two original messages are related by a small linear difference:

$$m_2 = m_1 + 58$$

**Given:** `chall.bin` containing $n$, $e$, $c_1$, $c_2$, and the difference value

## Solution

### Analysis
Standard RSA encryption is secure when messages are independent and padded correctly. However, when the same modulus is used to encrypt two messages with a known linear relationship, the system becomes vulnerable to the **Franklin-Reiter Related Message Attack**.

### Given Parameters
- **Modulus** ($n$): A large 1024-bit integer
- **Exponent** ($e$): $65537$
- **Ciphertexts**: $c_1$ and $c_2$
- **Relationship**: $m_2 = m_1 + 58$

### The Theory: Franklin-Reiter Attack

If we have two messages $m_1$ and $m_2$ such that $m_2 = f(m_1)$ for some linear function $f$, we can define two polynomials:

$$g_1(x) = x^e - c_1 \pmod{n}$$
$$g_2(x) = (x + 58)^e - c_2 \pmod{n}$$

Since $m_1$ is a root for both polynomials in the ring $\mathbb{Z}_n[x]$, the **Greatest Common Divisor (GCD)** of $g_1$ and $g_2$ will yield a linear factor $(x - m_1)$. By extracting the constant term from this linear factor, we recover the original message $m_1$.

### Solution Implementation (SageMath)

Because $e$ is large ($65537$), standard Python is too slow to handle these polynomial operations. SageMath is used to define a polynomial ring over the modular base and perform an efficient Euclidean algorithm.

```sage
from Crypto.Util.number import long_to_bytes

# Initializing parameters from challenge file 
n = 91838392436240503331712774858466175701943413315322225051619596529851993904079670234071457721426498873741584982531153498950691825618069096013454981926893433738150353153143279482383739121164274011329469871904925869165461464474403257196633053437505571229335243756784591951401736674559821793496918982152118235017
e = 65537
c1 = 4092240954031020785790852242303837214733355291076513085754622688235225835575277350063649697959294573249580037102991729522634639647348866656859757725636445738209685267524388862151853265672769726968577605819562167892539374143132425880944383491629187881404426192623442821140365568838900507845759302572175625919
c2 = 90832678244828575901502228077873044848423784837881215448557569301837036198770581553934213601743544299375081572394088859590937520703067629222089425569632363397430134047111700899828825903421330414123531257995919690385731463583767317272840450335992970852639723123504718994178146938027604531515234013744684414027
diff = 58

# Defining the Polynomial Ring over Zmod(n)
P.<x> = PolynomialRing(Zmod(n))
f1 = x^e - c1
f2 = (x + diff)^e - c2

# Function to perform GCD to find (x - m1)
def franklin_reiter(f1, f2):
    while f2 != 0:
        f1, f2 = f2, f1 % f2
    return -f1.coefficients()[0] / f1.coefficients()[1]

print("Calculating... this may take 1-5 minutes depending on CPU.")
m1 = franklin_reiter(f1, f2)
print(f"Flag: {long_to_bytes(int(m1)).decode()}")
```

### How It Works

1. **Polynomial Ring**: Create a polynomial ring over $\mathbb{Z}_n$
2. **Define Polynomials**: 
   - $f_1(x) = x^{65537} - c_1$
   - $f_2(x) = (x + 58)^{65537} - c_2$
3. **GCD Computation**: Use the Euclidean algorithm to find the GCD of $f_1$ and $f_2$
4. **Extract Root**: The GCD will be a linear polynomial of the form $ax - m_1$, from which we extract $m_1$
5. **Decode**: Convert $m_1$ from integer to bytes to get the flag

### Result
Running the script in SageMath (or WSL with SageMath installed) calculates the GCD and reveals the flag:

```
Flag: enigmaCTF26{RSA_R3L@T3D-MSGS_BR34K!}
```

## Flag
`enigmaCTF26{RSA_R3L@T3D-MSGS_BR34K!}`

## Key Takeaways
- **Never reuse the same RSA modulus** to encrypt related messages without strong, randomized padding (like OAEP)
- Even a small, known linear relationship (like a difference of 58) is enough to completely break the encryption
- The Franklin-Reiter attack exploits polynomial GCD to recover plaintexts when messages have a known linear relationship
- This demonstrates why proper padding schemes are critical in RSA implementations
- The flag "RSA_R3L@T3D-MSGS_BR34K!" directly references the vulnerability exploited