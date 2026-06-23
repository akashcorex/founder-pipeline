import os
import json
import urllib.request
import ssl

BUFFER_API_URL = "https://api.buffer.com"


def _load_env_vars():
    env_vars = {}
    env_path = "./.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    env_vars[key.strip()] = val.strip().strip('"').strip("'")
    return env_vars


def _graphql_request(query, variables=None):
    env_vars = _load_env_vars()
    api_key = env_vars.get("BUFFER_API_KEY")
    if not api_key:
        raise RuntimeError("BUFFER_API_KEY not found in .env")

    body = {"query": query}
    if variables:
        body["variables"] = variables

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        BUFFER_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, context=ctx) as res:
        result = json.loads(res.read().decode("utf-8"))

    if result.get("errors"):
        error = result["errors"][0]
        code = error.get("extensions", {}).get("code", "UNKNOWN")
        raise RuntimeError(f"Buffer API error ({code}): {error['message']}")

    return result.get("data")


def get_organizations():
    query = """
    query GetOrganizations {
      account {
        organizations {
          id
          name
        }
      }
    }
    """
    data = _graphql_request(query)
    return data["account"]["organizations"]


def get_channels(organization_id):
    query = """
    query GetChannels($orgId: String!) {
      channels(input: { organizationId: $orgId }) {
        id
        name
        service
      }
    }
    """
    data = _graphql_request(query, {"orgId": organization_id})
    return data["channels"]


def create_post(channel_id, text, due_at=None, mode="customScheduled", assets=None, metadata=None):
    scheduling_type = "automatic"
    if mode == "addToQueue":
        scheduling_type = "automatic"

    input_obj = {
        "text": text,
        "channelId": channel_id,
        "schedulingType": scheduling_type,
        "mode": mode,
    }

    if due_at:
        input_obj["dueAt"] = due_at

    if assets:
        input_obj["assets"] = assets

    if metadata:
        input_obj["metadata"] = metadata

    query = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post {
            id
            text
            dueAt
            status
          }
        }
        ... on MutationError {
          message
        }
      }
    }
    """

    data = _graphql_request(query, {"input": input_obj})
    result = data["createPost"]

    if result.get("post"):
        return result["post"]
    elif result.get("message"):
        raise RuntimeError(f"Buffer mutation error: {result['message']}")
    else:
        raise RuntimeError(f"Unexpected Buffer response: {result}")


def delete_post(post_id):
    query = """
    mutation DeletePost($id: ID!) {
      deletePost(id: $id) {
        ... on Post {
          id
        }
        ... on MutationError {
          message
        }
      }
    }
    """
    data = _graphql_request(query, {"id": post_id})
    result = data["deletePost"]
    if result.get("message"):
        raise RuntimeError(f"Buffer mutation error: {result['message']}")
    return result


def get_posts(organization_id, status_filter=None, channel_ids=None, first=50):
    filter_input = {}
    if status_filter:
        filter_input["status"] = status_filter
    if channel_ids:
        filter_input["channelIds"] = channel_ids

    query = """
    query GetPosts($orgId: String!, $first: Int!, $filter: PostsFilterInput) {
      posts(
        first: $first,
        input: { organizationId: $orgId, filter: $filter }
      ) {
        edges {
          node {
            id
            text
            dueAt
            channelId
            status
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    variables = {
        "orgId": organization_id,
        "first": first,
        "filter": filter_input if filter_input else None,
    }
    data = _graphql_request(query, variables)
    edges = data["posts"]["edges"]
    return [edge["node"] for edge in edges]
