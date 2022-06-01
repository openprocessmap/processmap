# Process Map

A Python library to represent process and task networks, specifically geared towards simulation of logistic processes

## To do

- Using resources
- Simple runs
- Merges
- ChooseMap() using Simulation Variable
- Visualization
- Syntactic sugar

## Process Map operations

### `Chain A and B`

`B` can start only after `A` has ended.

Note: `Chain A and (Chain B and C)` will flatten to `Chain [A, B, C]` 

### `Chain Iterable[A]`

Each process in `A` can only start after the previous process has ended

### `Chain Iterable[A] and Iterable[B]`

All processes `B` can only start after all processes `A` have ended.

### `Chain Iterable[Iterable[A]]`

Each collection of processes in `A` can only start after all the processes in the previous collection have ended.

### `Link A and B`

`A` can end only once `B` has started.

### `Link Iterable[A]`

### `Link Iterable[A] and Iterable[B]`

All processes `A` can end only after all processes `B` have started.

### `Link Iterable[Iterable[A]]`

### `Parallelize Iterable[A]`

Allow all processes `A` to happen simultaneously and independently in a wrapper process.
All processes can start once the wrapping process has started,
and the wrapping process can end once all wrapped processes have ended.

### `A Using R`

`A` can only start once a resource request has been granted.
`R` is released once A has ended.

Note: `A Using R Using S` will be flattened to `A Using [R, S]`.
This means that the resource requests will be parallelized.
To prevent this behavior use `UsingSeparately`.

Note: Note that releasing resources will happen succesfully and instantaneously.
No process ever has to wait to release a resource sucessfully.

### `A Using Iterable[R]`

`A` can only start once all resource requests for `A` have been granted.
`A` can only end once all resource requests are succesfully released.
Resource requests and resource releases are parallelized.

### `A UsingSeparately R Using S`
### `A Using R UsingSeparately S`
### `A UsingSeparately R UsingSeparately S`

In the above cases `A` can start only when resource `R` has been granted,
but resource `R` can only be requested once resource `S` has been granted.

Conversely, resource `S` can only bre released once resource `R` has been succesfully released.

Use `UsingSeparately` to prevent resource requests and releases to be handled in parallel.

### `Merge A and B with buffer X`

The resulting process is the union of both processes.
Any dependencies between `A` and `B` are created only by having common process maps nested in `A` and `B`.

When this leads to multiple starting points for the resulting process the difference in starting time is calculated
and appropriate wait processes are inserted before the later starting points.
The buffer time is subtracted from the duration of these waiting processes.

### `Meld A and B`

Processes `A` and `B` can start and end only at the same time.
Any resource requests and releases from the outer `Using` clause must all be satisfied before starting and ending.
`UsingSeparately` clauses are not considered, nor are `Using` clauses inside `UsingSeparately` clauses.
