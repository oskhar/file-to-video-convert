# Pseudo Code Reed-Solomon Algoritm

## Encode Proses

```
function ReedSolomonEncode(data, n, k)
    generator ← [1, alpha, alpha^2, ..., alpha^(n-k-1)]
    message ← data + [0] * (n - k)

    for i from 0 to k-1 do
        if message[i] ≠ 0 then
            for j from 0 to n-k do
                message[i+j] ← message[i+j] XOR gf_mult(generator[j], message[i])
            end for
        end if
    end for

    codeword ← data + message[k:]
    return codeword
end function

function gf_mult(a, b)
    return gf_mult_table[a][b]
end function
```

## Decode Proses

```
function ReedSolomonDecode(received, n, k)
    syndromes ← [0] * (n - k)
    for i from 0 to n-k-1 do
        syndromes[i] ← EvaluatePolynomial(received, alpha^i)
    end for

    if all(syndrome = 0 for syndrome in syndromes) then
        return received[:k]
    end if

    errorLocator ← BerlekampMassey(syndromes)

    errorPositions ← []
    for i from 0 to n-1 do
        if EvaluatePolynomial(errorLocator, alpha^-i) = 0 then
            errorPositions.append(i)
        end if
    end for

    errorMagnitudes ← ForneysAlgorithm(syndromes, errorLocator, errorPositions)

    corrected ← received[:]
    for i from 0 to length(errorPositions)-1 do
        corrected[errorPositions[i]] ← corrected[errorPositions[i]] XOR errorMagnitudes[i]
    end for

    return corrected[:k]
end function
```
