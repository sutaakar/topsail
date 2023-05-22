import datetime
import logging
import sys

from toolbox._common import RunAnsibleRole, AnsibleRole, AnsibleMappedParams, AnsibleConstant, AnsibleSkipConfigGeneration

class Local_CI:
    """
    Commands to run the CI scripts in a container environment similar to the one used by the CI
    """

    @AnsibleRole("local_ci_run")
    @AnsibleMappedParams
    def run(self, ci_command,
            pr_number=None,
            git_repo="https://github.com/openshift-psap/ci-artifacts",
            git_ref="main",
            namespace="ci-artifacts",
            istag="ci-artifacts:main",
            pod_name="ci-artifacts",
            service_account="default",
            secret_name=None,
            secret_env_key=None,
            init_command=None,
            export_command=None,
            export_identifier="default",
            export_ts_id=None,
            export=True,
            retrieve_artifacts=True,
            pr_config=None,
            update_git=True,
            ):
        """
        Runs a given CI command

        Args:
            git_repo: The Github repo to use.
            git_ref: The Github ref to use.
            pr_number: The ID of the PR to use for the repository.
            ci_command: The CI command to run.
            namespace: The namespace in which the image.
            istag: The imagestream tag to use.
            pod_name: The name to give to the Pod running the CI command.
            service_account: Name of the ServiceAccount to use for running the Pod.
            secret_name: Name of the Secret to mount in the Pod.
            secret_env_key: Name of the environment variable with which the secret path will be exposed in the Pod.
            init_command: Command to run in the container before running anything else.
            export_identifier: Identifier of the test being executed (will be a dirname).
            export_ts_id: Timestamp identifier of the test being executed (will be a dirname).
            export_command: Command to run to export the execution artifacts to a external storage.
            export: If False, do not run the export command.
            retrieve_artifacts: If False, do not retrieve locally the test artifacts.
            pr_config: Optional path to a PR config file (avoids fetching Github PR json).
            update_git: If True, updates the git repo with the latest main/PR before running the test.
        """

        if pr_number and not update_git:
            logging.error(f"Cannot have --pr-number={pr_number} without --update-git")
            sys.exit(1)

        if not export_ts_id:
            export_ts_id = datetime.datetime.now().strftime("%Y%m%d_%H%M")

        return RunAnsibleRole(locals())

    @AnsibleRole("local_ci_run_multi")
    @AnsibleMappedParams
    def run_multi(self, ci_command,
                  user_count: int = 1,
                  namespace="ci-artifacts",
                  istag="ci-artifacts:main",
                  job_name="ci-artifacts",
                  service_account="default",
                  secret_name=None,
                  secret_env_key=None,
                  retrieve_artifacts=False,
                  minio_namespace=None,
                  minio_bucket_name=None,
                  minio_secret_key_key=None,
                  pr_config=None,
                  capture_prom_db: bool = True,
                  git_pull: bool = False,
                  state_signal_redis_server=None,
                  ):
        """
        Runs a given CI command in parallel from multiple Pods

        Args:
            ci_command: The CI command to run.
            namespace: The namespace in which the image.
            istag: The imagestream tag to use.
            job_name: The name to give to the Job running the CI command.
            service_account: Name of the ServiceAccount to use for running the Pod.
            secret_name: Name of the Secret to mount in the Pod.
            secret_env_key: Name of the environment variable with which the secret path will be exposed in the Pod.
            retrieve_artifacts: If False, do not retrieve locally the test artifacts.
            minio_namespace: Namespace where the Minio server is located.
            minio_bucket_name: Name of the bucket in the Minio server.
            minio_secret_key_key: Key inside 'secret_env_key' containing the secret to access the Minio bucket. Must be in the form 'user_password=SECRET_KEY'.
            pr_config: Optional path to a PR config file (avoids fetching Github PR json).
            capture_prom_db: If True, captures the Prometheus DB of the systems.
            git_pull: If True, update the repo in the image with the latest version of the build ref before running the command in the Pods.
            state_signal_redis_server: Optional address of the Redis server to pass to StateSignal synchronization.
        """

        if retrieve_artifacts and not (minio_namespace and minio_bucket_name):
            logging.error(f"--minio_namespace and --minio_bucket_name must be provided when --retrieve_artifacts is enabled")
            sys.exit(1)

        return RunAnsibleRole(locals())