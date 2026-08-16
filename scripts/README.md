# Instructor Scripts

This folder contains reproducible utilities supporting the nine-hour seminar, its thirty modules, and its public-data teaching activities. The scripts are designed as inspectable instructor artefacts rather than opaque automation.

| Script | Purpose |
|---|---|
| [`build_nine_hour_curriculum.py`](./build_nine_hour_curriculum.py) | Generates the authoritative 3-day, 30-module manifest and the detailed seminar-design document. |
| [`validate_curriculum_data.py`](./validate_curriculum_data.py) | Confirms that the curriculum has three days, ten modules per day, one demonstrated dataset and 3–5 distinct public BYOD datasets per module, a participant-upload route, and available local public data files. |

The planned `session*` scripts will supply additional instructor demonstrations for specific modules. Every future script should state inputs, software requirements, expected outputs, and pedagogical role. Scripts must not contain credentials or export participant-uploaded data outside the documented in-memory workshop environment.
