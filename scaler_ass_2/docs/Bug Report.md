**Bug 1: Memory Limit Conflict (2x Rule vs. cgroup Cap)**

* **Description:** A process in the **CRITICAL** class is subject to a required 2x memory limit increase (e.g., 8 GB base \* 2 \= 16 GB). However, the underlying **cgroup** for the **CRITICAL** class is strictly capped at 8 GB. This conflict causes the kernel to prematurely terminate the process with an **Out-of-Memory (OOM)** error before it can reach the calculated 16 GB limit. The core ambiguity is whether the resource-specific 2x rule should override the class's cgroup cap or if the cgroup cap must be dynamically expanded to accommodate the rule.  
* **Steps to Reproduce:**  
  1. Place a process in the **CRITICAL** class.  
  2. Set the base memory limit to 8 GB.  
  3. Trigger the 2x memory increase logic (expected limit: 16 GB).  
  4. Observe the process termination by OOM killer due to the 8 GB cgroup cap.  
* **Observed Result:** Process is terminated with OOM error at 8 GB usage.  
* **Expected Result:** Process should be allowed to use up to the calculated 16 GB limit.


**Bug 2: Ulimit and cgroup Inconsistency**

* **Description:** An incompatibility exists between process-level **ulimit \-u** settings and system-wide user limits. The Resource Manager may set a high process limit (e.g., **4096**) for a critical process, but if the process's associated user has a lower system-wide limit (e.g., **1024**), the lower system-wide limit prevails, causing a resource constraint.  
* **Steps to Reproduce:**  
  1. Set the system-wide process limit for a user to a low value (e.g., 1024).  
  2. Use the Resource Manager to launch a critical process under that user and set its individual **ulimit \-u** to a higher value (e.g., 4096).  
  3. Attempt to spawn more than 1024 threads/processes under the critical process.  
* **Observed Result:** The process fails to create new resources once the 1024 limit is reached.  
* **Expected Result:** The process should adhere to the limit set by the Resource Manager (4096).


**Bug 3: Incorrect Memory Allocation on Process Downgrade**

* **Description:** When a database process is downgraded from the **STANDARD** class to the **BEST\_EFFORT** class, the memory limit is incorrectly halved. Instead of maintaining the required limit of 1024 MB (which is presumed to be the value before downgrade), the process is assigned the default lower limit of 512 MB. This indicates a loss of the current limit's state or an incorrect application of a "default" limit during rebalancing/downgrade.  
* **Steps to Reproduce:**  
  1. Create a process named `postgres_db`.  
  2. Update the process's usage to trigger a downgrade from **STANDARD** to **BEST\_EFFORT**.  
  3. Check the `resources.memoryLimit` after the rebalancing operation.  
* **Observed Result:** 512 MB.  
* **Expected Result:** 1024 MB (The limit should either be maintained or correctly calculated based on the new class's rules, which, based on the description, is 1024 MB).


Bug 4:**performance starvation**

**The Bug:** There is no rule for a process in `BEST_EFFORT` using **30% CPU**.

**Scenario:** A process starts in `STANDARD`, drops to 15% CPU (downgraded to `BEST_EFFORT`), then its load increases to 35%.

**Result:** It is now performing a "standard" workload but is being choked by `BEST_EFFORT` limits. Because it hasn't hit the \>50% "Upgrade" trigger, it stays throttled forever. This is a "Performance Starvation" bug.

