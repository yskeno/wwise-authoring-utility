using System;
using System.Collections.Generic;
using System.Diagnostics.Metrics;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Threading.Tasks;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace AK.Wwise.Waapi
{
    public class ClientUtility
    {
        private AK.Wwise.Waapi.Client client = new();

        public delegate void PublishHandler(JsonObject json);
        public event Wamp.DisconnectedHandler Disconnected;

        public ClientUtility()
        {
            client.Disconnected += Client_Disconnected;
        }

        private void Client_Disconnected()
        {
            if (Disconnected != null)
            {
                Disconnected();
            }
        }

        /// <summary>Connect to a running instance of Wwise Authoring.</summary>
        /// <param name="uri">URI to connect. Usually the WebSocket protocol (ws:) followed by the hostname and port, followed by waapi.</param>
        /// <example>Connect("ws://localhost:8080/waapi")</example>
        /// <param name="timeout">The maximum timeout in milliseconds for the function to execute. Will raise Waapi.TimeoutException when timeout is reached.</param>
        public async Task Connect(string uri = "ws://localhost:8080/waapi",
                                  int timeout = int.MaxValue)
        {
            await client.Connect(uri, timeout);
        }

        /// <summary>Close the connection.</summary>
        /// <param name="timeout">The maximum timeout in milliseconds for the function to execute. Will raise Waapi.TimeoutException when timeout is reached.</param>
        public async Task Close()
        {
            await client.Close();
        }

        /// <summary>
        /// Return true if the client is connected and ready for operations.
        /// </summary>
        public bool IsConnected()
        {
            return client.IsConnected();
        }

        /// <summary>
        /// Call a WAAPI remote procedure. Refer to WAAPI reference documentation for a list of URIs and their arguments and options.
        /// </summary>
        /// <param name="uri">The URI of the remote procedure.</param>
        /// <param name="args">The arguments of the remote procedure. C# anonymous objects will be automatically serialized to Json.</param>
        /// <param name="options">The options the remote procedure. C# anonymous objects will be automatically serialized to Json.</param>
        /// <param name="timeout">The maximum timeout in milliseconds for the function to execute. Will raise Waapi.TimeoutException when timeout is reached.</param>
        /// <returns>A Newtonsoft.Json.Linq.JObject with the result of the Remote Procedure Call.</returns>
        public async Task<JsonObject> Call(string uri,
                                           object? args = null,
                                           object? options = null,
                                           int timeout = int.MaxValue)
        {
            args ??= new { };
            options ??= new { };

            return await Call(uri,
                              JsonNode.Parse(JsonSerializer.Serialize(args))!.AsObject(),
                              JsonNode.Parse(JsonSerializer.Serialize(options))!.AsObject(),
                              timeout);
        }

        /// <summary>
        /// Call a WAAPI remote procedure. Refer to WAAPI reference documentation for a list of URIs and their arguments and options.
        /// </summary>
        /// <param name="uri">The URI of the remote procedure.</param>
        /// <param name="args">The arguments of the remote procedure as a Newtonsoft.Json.Linq.JObject</param>
        /// <param name="options">The options the remote procedure as a Newtonsoft.Json.Linq.JObject.</param>
        /// <param name="timeout">The maximum timeout in milliseconds for the function to execute. Will raise Waapi.TimeoutException when timeout is reached.</param>
        /// <returns>A Newtonsoft.Json.Linq.JObject with the result of the Remote Procedure Call.</returns>
        public async Task<JsonObject> Call(string uri,
                                           JsonObject? args,
                                           JsonObject? options,
                                           int timeout = int.MaxValue)
        {
            args ??= [];
            options ??= [];

            string result = await client.Call(uri,
                                              args.ToString(),
                                              options.ToString(),
                                              timeout);

            return JsonNode.Parse(result)!.AsObject();
        }

        /// <summary>
        /// Subscribe to a topic. Refer to WAAPI reference documentation to obtain the list of topics available.
        /// </summary>
        /// <param name="topic">Topic to subscribe</param>
        /// <param name="options">Option for the subscrition.</param>
        /// <param name="publishHandler">Delegate that will be executed when the topic is pusblished.</param>
        /// <param name="timeout">The maximum timeout in milliseconds for the function to execute. Will raise Waapi.TimeoutException when timeout is reached.</param>
        /// <returns></returns>
        public async Task<int> Subscribe(string topic,
                                         object? options,
                                         PublishHandler publishHandler,
                                         int timeout = int.MaxValue)
        {
            options ??= new { };

            return await Subscribe(topic,
                                   JsonNode.Parse(JsonSerializer.Serialize(options))!.AsObject(),
                                   publishHandler,
                                   timeout);
        }

        /// <summary>
        /// Subscribe to a topic. Refer to WAAPI reference documentation to obtain the list of topics available.
        /// </summary>
        /// <param name="topic">Topic to subscribe</param>
        /// <param name="options">Option for the subscrition.</param>
        /// <param name="publishHandler">Delegate that will be executed when the topic is pusblished.</param>
        /// <param name="timeout">The maximum timeout in milliseconds for the function to execute. Will raise Waapi.TimeoutException when timeout is reached.</param>
        /// <returns>The subscription id assigned to the subscription. Store the id to call Unsubscribe.</returns>
        public async Task<int> Subscribe(string topic,
                                         JsonObject? options,
                                         PublishHandler publishHandler,
                                         int timeout = int.MaxValue)
        {
            options ??= [];

            return await client.Subscribe(topic,
                                          options.ToString(),
                                          (string json) => publishHandler(JsonNode.Parse(json)!.AsObject()),
                                          timeout);
        }

        /// <summary>
        /// Unsubscribe from a subscription.
        /// </summary>
        /// <param name="subscriptionId">The subscription id received from the initial subscription.</param>
        /// <param name="timeout">The maximum timeout in milliseconds for the function to execute. Will raise Waapi.TimeoutException when timeout is reached.</param>
        public async Task Unsubscribe(int subscriptionId, int timeout = int.MaxValue)
        {
            await client.Unsubscribe(subscriptionId, timeout);
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            _Main().Wait();
        }

        static async Task _Main()
        {
            try
            {
                ClientUtility client = new ClientUtility();

                // Try to connect to running instance of Wwise on localhost, default port
                await client.Connect();

                // Register for connection lost event
                client.Disconnected += () =>
                {
                    Console.WriteLine("We lost connection!");
                };

                // Simple RPC call
                var info = await client.Call(ak.wwise.core.getInfo, null, null);
                Console.WriteLine(info.ToString());

                // Create an object for our tests, using C# anonymous types
                var testObj = await client.Call(ak.wwise.core.@object.create,
                                                new
                                                {
                                                    name = "WaapiObject",
                                                    parent = @"\Actor-Mixer Hierarchy\Default Work Unit",
                                                    type = "ActorMixer",
                                                    onNameConflict = "rename"
                                                },
                                                null);
                Console.WriteLine(testObj!["id"]!.ToString());

                // Subscribe to name changes
                int nameSubscriptionId = await client.Subscribe(ak.wwise.core.@object.nameChanged,
                                                                null,
                                                                (JsonObject publication) =>
                                                                {
                                                                    Console.WriteLine($"Name changed: {publication!.ToString()}");
                                                                });

                // Subscribe to property changes
                int propertySubscriptionId = await client.Subscribe(ak.wwise.core.@object.propertyChanged,
                                                                    new JsonObject
                                                                    {
                                                                        ["property"] = JsonValue.Create("Volume"),
                                                                        ["object"] = JsonValue.Create(testObj["id"]!.ToString())
                                                                    },
                                                                    (JsonObject publication) =>
                                                                    {
                                                                        Console.WriteLine($"Property '{publication["property"]!.ToString()}' changed: {publication["new"]!.ToString()}");
                                                                    });


                // Set name using C# anonymous types
                try
                {
                    await client.Call(ak.wwise.core.@object.setName,
                                      new
                                      {
                                          @object = testObj["id"],
                                          value = "NewName"
                                      },
                                      null);

                    // Undo the set name, using JObject constructor
                    await client.Call(ak.wwise.ui.commands.execute,
                                      new JsonObject { ["command"] = JsonValue.Create("Undo") },
                                      null);
                }
                catch (AK.Wwise.Waapi.Wamp.ErrorException e)
                {
                    Console.Write(e.Message);
                    // Ignore the error, it is possible we have a name conflict
                }

                // Set property using anonymous type
                await client.Call(ak.wwise.core.@object.setProperty,
                                  new
                                  {
                                      @property = "Volume",
                                      @object = testObj["id"],
                                      value = 6
                                  },
                                  null);

                // Not support dynamic types
                // Setting a property using dynamic types
                //{
                //    dynamic args = new JsonObject();
                //    args.property = "Volume";
                //    args.@object = testObj["id"];
                //    args.value = 9;

                //    // Set property with JObject
                //    await client.Call(ak.wwise.core.@object.setProperty, args, null);
                //}

                // Setting a property using JObject constructor
                await client.Call(ak.wwise.core.@object.setProperty,
                                  new JsonObject
                                  {
                                      ["property"] = JsonValue.Create("Volume"),
                                      ["object"] = JsonValue.Create(testObj["id"]!.ToString()),
                                      ["value"] = JsonValue.Create(10)
                                  },
                                  null);

                {
                    // Query the volume, using JObject constructor
                    var query = new JsonObject
                    {
                        ["from"] = new JsonObject
                        {
                            ["id"] = new JsonArray { testObj["id"]!.ToString() }
                        }
                    };

                    var options = new JsonObject
                    {
                        ["return"] = new JsonArray { "name", "id", "@Volume" }
                    };

                    Console.WriteLine(query.ToJsonString());
                    Console.WriteLine(options.ToJsonString());
                    var result = await client.Call(ak.wwise.core.@object.get, query, options);
                    Console.WriteLine(result!["return"]![0]!["@Volume"]!.ToString());
                }

                {
                    // Query the project using anonymous objects
                    var query = new
                    {
                        from = new
                        {
                            id = new string[] { testObj["id"]!.ToString() }
                        }
                    };
                    var options = new
                    {
                        @return = new string[] { "name", "id", "@Volume", "path" }
                    };

                    var jresult = await client.Call(ak.wwise.core.@object.get, query, options);
                    Console.WriteLine(jresult!["return"]![0]!["@Volume"]!.ToString());
                }

                // Clean up the created objects!
                await client.Call(ak.wwise.core.@object.delete,
                                  new JsonObject { ["object"] = JsonValue.Create(testObj["id"]!.ToString()) },
                                  null);

                await client.Unsubscribe(nameSubscriptionId);
                await client.Unsubscribe(propertySubscriptionId);

                await client.Close();

                Console.WriteLine("done");
            }
            catch (Exception e)
            {
                Console.Error.WriteLine($"ERROR: {e.Message}");
            }
        }
    }
}